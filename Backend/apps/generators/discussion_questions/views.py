"""
Django Views for Discussion Questions Generation
Supports both streaming responses and background jobs.
"""

import json
import uuid
import os
from django.http import JsonResponse, StreamingHttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .logic import DiscussionQuestionsInput, DiscussionQuestionsGenerator, generate_discussion_questions_from_dict
from .llm_client import get_llm_client
from .docx_export import export_discussion_questions_to_docx


# In-memory job storage (use Redis/DB in production)
_jobs = {}


@csrf_exempt
@require_http_methods(["POST"])
def generate_discussion_questions_view(request):
    """
    Generate discussion questions (streaming response).
    
    POST body:
    {
        "category": "Science",
        "topic": "Food Safety",
        "grade_level": "Middle",
        "num_questions": 3,
        "teacher_details": "optional context"
    }
    
    Returns:
    {
        "success": true,
        "output": "generated text",
        "attempts": 1
    }
    """
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    
    # Validate required fields
    required = ['category', 'topic', 'grade_level', 'num_questions']
    missing = [f for f in required if f not in data]
    if missing:
        return JsonResponse({
            'success': False,
            'error': f'Missing required fields: {", ".join(missing)}'
        }, status=400)
    
    # Validate grade_level
    if data['grade_level'] not in ['Elementary', 'Middle', 'High', 'College']:
        return JsonResponse({
            'success': False,
            'error': f'Invalid grade_level: {data["grade_level"]}'
        }, status=400)
    
    # Validate num_questions
    try:
        num_q = int(data['num_questions'])
        if not (1 <= num_q <= 5):
            raise ValueError()
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'error': f'num_questions must be integer 1-5, got: {data.get("num_questions")}'
        }, status=400)
    
    # Use streaming response to keep connection alive
    def generate():
        try:
            # Create LLM client
            llm_client = get_llm_client()
            
            # Generate using new implementation
            result = generate_discussion_questions_from_dict(
                llm_client=llm_client,
                inputs=data,
                max_attempts=3
            )
            
            response_data = {
                'success': True,
                'output': result['output'],
                'attempts': result['attempts']
            }
            
            yield json.dumps(response_data)
        
        except ValueError as e:
            error_response = {
                'success': False,
                'error': str(e)
            }
            yield json.dumps(error_response)
        
        except Exception as e:
            error_response = {
                'success': False,
                'error': f'Internal error: {str(e)}'
            }
            yield json.dumps(error_response)
    
    return StreamingHttpResponse(
        generate(),
        content_type='application/json'
    )


@csrf_exempt
@require_http_methods(["POST"])
def submit_discussion_questions_job(request):
    """
    Submit background job for discussion questions generation.
    
    POST body: same as generate_discussion_questions_view
    
    Returns:
    {
        "job_id": "uuid",
        "status": "pending"
    }
    """
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    
    # Validate required fields
    required = ['category', 'topic', 'grade_level', 'num_questions']
    missing = [f for f in required if f not in data]
    if missing:
        return JsonResponse({
            'success': False,
            'error': f'Missing required fields: {", ".join(missing)}'
        }, status=400)
    
    # Validate inputs
    if data['grade_level'] not in ['Elementary', 'Middle', 'High', 'College']:
        return JsonResponse({
            'success': False,
            'error': f'Invalid grade_level: {data["grade_level"]}'
        }, status=400)
    
    try:
        num_q = int(data['num_questions'])
        if not (1 <= num_q <= 5):
            raise ValueError()
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'error': f'num_questions must be integer 1-5'
        }, status=400)
    
    # Create job
    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        'status': 'pending',
        'data': data,
        'result': None,
        'error': None
    }
    
    # Start background task
    import threading
    thread = threading.Thread(
        target=_process_discussion_questions_job,
        args=(job_id,)
    )
    thread.daemon = True
    thread.start()
    
    return JsonResponse({
        'job_id': job_id,
        'status': 'pending'
    })


def _process_discussion_questions_job(job_id: str):
    """Background worker for processing job."""
    
    job = _jobs.get(job_id)
    if not job:
        return
    
    job['status'] = 'processing'
    
    try:
        data = job['data']
        
        llm_client = get_llm_client()
        result = generate_discussion_questions_from_dict(
            llm_client=llm_client,
            inputs=data,
            max_attempts=3
        )
        
        job['status'] = 'completed'
        job['result'] = result
    
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)


@require_http_methods(["GET"])
def get_discussion_questions_job_status(request, job_id):
    """
    Get status of background job.
    
    Returns:
    {
        "job_id": "uuid",
        "status": "pending|processing|completed|failed",
        "result": {...} (if completed),
        "error": "..." (if failed)
    }
    """
    
    job = _jobs.get(job_id)
    if not job:
        return JsonResponse({
            'error': 'Job not found'
        }, status=404)
    
    response = {
        'job_id': job_id,
        'status': job['status']
    }
    
    if job['status'] == 'completed':
        response['result'] = job['result']
    elif job['status'] == 'failed':
        response['error'] = job['error']
    
    return JsonResponse(response)


@csrf_exempt
@require_http_methods(["POST"])
def export_discussion_questions_docx(request):
    """
    Export discussion questions to DOCX.
    
    POST body:
    {
        "questions_text": "generated discussion questions text"
    }
    
    Returns: DOCX file download
    """
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    
    if 'questions_text' not in data:
        return JsonResponse({
            'success': False,
            'error': 'Missing questions_text field'
        }, status=400)
    
    try:
        # Create temporary file
        output_dir = getattr(settings, 'DISCUSSION_QUESTIONS_OUTPUT_DIR', '/tmp')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f'discussion_questions_{uuid.uuid4()}.docx')
        
        # Export to DOCX
        template_path = getattr(settings, 'DISCUSSION_QUESTIONS_TEMPLATE_PATH', None)
        title_style = getattr(settings, 'DISCUSSION_QUESTIONS_TITLE_STYLE', 'Title')
        body_style = getattr(settings, 'DISCUSSION_QUESTIONS_BODY_STYLE', 'Normal')
        
        export_discussion_questions_to_docx(
            questions_text=data['questions_text'],
            output_path=output_path,
            template_path=template_path,
            title_style=title_style,
            body_style=body_style
        )
        
        # Return file
        response = FileResponse(
            open(output_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="discussion_questions.docx"'
        
        return response
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Export failed: {str(e)}'
        }, status=500)
