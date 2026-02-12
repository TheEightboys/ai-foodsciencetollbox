"""
Django Views for Learning Objectives Generation
Supports both streaming responses and background jobs.
"""

import json
import uuid
import os
from django.http import JsonResponse, StreamingHttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from .logic import LearningObjectivesInput, LearningObjectivesGenerator, generate_learning_objectives
from .llm_client import get_llm_client
from .docx_export import export_learning_objectives_to_docx


# In-memory job storage (use Redis/DB in production)
_jobs = {}


@csrf_exempt
@require_http_methods(["POST"])
def generate_learning_objectives_view(request):
    """
    Generate learning objectives (streaming response).
    
    POST body:
    {
        "category": "Science",
        "topic": "Food Safety",
        "grade_level": "Middle",
        "teacher_details": "optional context",
        "num_objectives": 5
    }
    
    Returns:
    {
        "success": true,
        "grade_level": "Middle",
        "topic": "Food Safety",
        "objectives": ["...", "..."],
        "rendered_text": "full formatted text",
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
    required = ['category', 'topic', 'grade_level']
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
    
    # Validate num_objectives
    num_objectives = data.get('num_objectives', 5)
    try:
        num_objectives = int(num_objectives)
        if not (4 <= num_objectives <= 10):
            raise ValueError()
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'error': f'num_objectives must be integer 4-10, got: {num_objectives}'
        }, status=400)
    
    # Use streaming response to keep connection alive
    def generate():
        try:
            # Create inputs
            inputs = LearningObjectivesInput(
                category=data['category'],
                topic=data['topic'],
                grade_level=data['grade_level'],
                teacher_details=data.get('teacher_details'),
                num_objectives=num_objectives
            )
            
            # Generate
            llm_client = get_llm_client()
            generator = LearningObjectivesGenerator(
                llm_client=llm_client,
                max_attempts=3
            )
            
            result = generator.generate(inputs)
            
            response_data = {
                'success': True,
                'grade_level': result['grade_level'],
                'topic': result['topic'],
                'objectives': result['objectives'],
                'rendered_text': result['rendered_text'],
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
def submit_learning_objectives_job(request):
    """
    Submit background job for learning objectives generation.
    
    POST body: same as generate_learning_objectives_view
    
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
    required = ['category', 'topic', 'grade_level']
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
    
    num_objectives = data.get('num_objectives', 5)
    try:
        num_objectives = int(num_objectives)
        if not (4 <= num_objectives <= 6):
            raise ValueError()
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'error': f'num_objectives must be integer 4-6'
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
        target=_process_learning_objectives_job,
        args=(job_id,)
    )
    thread.daemon = True
    thread.start()
    
    return JsonResponse({
        'job_id': job_id,
        'status': 'pending'
    })


def _process_learning_objectives_job(job_id: str):
    """Background worker for processing job."""
    
    job = _jobs.get(job_id)
    if not job:
        return
    
    job['status'] = 'processing'
    
    try:
        data = job['data']
        
        inputs = LearningObjectivesInput(
            category=data['category'],
            topic=data['topic'],
            grade_level=data['grade_level'],
            teacher_details=data.get('teacher_details'),
            num_objectives=int(data.get('num_objectives', 5))
        )
        
        llm_client = get_llm_client()
        generator = LearningObjectivesGenerator(
            llm_client=llm_client,
            max_attempts=3
        )
        
        result = generator.generate(inputs)
        
        job['status'] = 'completed'
        job['result'] = result
    
    except Exception as e:
        job['status'] = 'failed'
        job['error'] = str(e)


@require_http_methods(["GET"])
def get_learning_objectives_job_status(request, job_id):
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
def export_learning_objectives_docx(request):
    """
    Export learning objectives to DOCX.
    
    POST body:
    {
        "grade_level": "Middle",
        "topic": "Food Safety",
        "objectives": ["...", "..."]
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
    
    required = ['grade_level', 'topic', 'objectives']
    missing = [f for f in required if f not in data]
    if missing:
        return JsonResponse({
            'success': False,
            'error': f'Missing required fields: {", ".join(missing)}'
        }, status=400)
    
    try:
        # Create temporary file
        output_dir = getattr(settings, 'LEARNING_OBJECTIVES_OUTPUT_DIR', '/tmp')
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, f'learning_objectives_{uuid.uuid4()}.docx')
        
        # Export to DOCX
        template_path = getattr(settings, 'LEARNING_OBJECTIVES_TEMPLATE_PATH', None)
        title_style = getattr(settings, 'LEARNING_OBJECTIVES_TITLE_STYLE', 'Title')
        body_style = getattr(settings, 'LEARNING_OBJECTIVES_BODY_STYLE', 'Normal')
        list_style = getattr(settings, 'LEARNING_OBJECTIVES_LIST_STYLE', 'List Number')
        
        export_learning_objectives_to_docx(
            grade_level=data['grade_level'],
            topic=data['topic'],
            objectives=data['objectives'],
            output_path=output_path,
            template_path=template_path,
            title_style=title_style,
            body_style=body_style,
            list_style=list_style
        )
        
        # Return file
        response = FileResponse(
            open(output_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename="learning_objectives.docx"'
        
        return response
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Export failed: {str(e)}'
        }, status=500)
