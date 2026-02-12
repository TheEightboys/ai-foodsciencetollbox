import apiClient from './client';

export interface GenerationRequest {
  // NEW CONSOLIDATED DESIGN: Single prompt with user_intent
  user_intent?: string;
  grade_level: string;
  num_objectives?: number;
  
  // LEGACY FIELDS: Accepted but ignored for backward compatibility
  subject?: string;
  topic?: string;
  number_of_objectives?: number;
  customization?: string;
  additional_context?: string;
  content_type: 'lesson_starter' | 'learning_objectives' | 'discussion_questions' | 'quiz' | 'worksheet' | 'rubric' | 'lesson_plan' | 'slide' | 'activity' | 'lab';
  [key: string]: any; // For additional generator-specific fields
}

export interface GeneratedContent {
  id: number;
  title: string;
  content: string;
  content_type: string;
  tokens_used: number;
  is_favorite: boolean;
  created_at: string;
  updated_at: string;
}

export interface GenerationResponse {
  content: string;
  tokens_used: number;
  generation_time?: number;
  id?: number;
  formatted_docx_url?: string;
  formatted_pdf_url?: string;
  
  // NEW CONSOLIDATED SYSTEM: Enhanced response data
  objectives?: string[];
  grade_level?: string;
  topic?: string;
  routing_info?: {
    domain: string;
    confidence: number;
    apply_food_overlay: boolean;
    domain_description: string;
    fallback_used?: boolean;
  };
  quality_metrics?: {
    objectives_generated: number;
    target_objectives: number;
    grade_level_match: boolean;
    domain_confidence: number;
    has_food_overlay: boolean;
    fallback_used?: boolean;
  };
  warnings?: string[];
  observability?: {
    generation_time: number;
    total_generation_time: number;
    attempts: number;
    success: boolean;
    fallback_used?: boolean;
  };
}

class GeneratorService {
  async generateLessonStarter(data: {
    // NEW FORMAT: 7 lesson starter ideas, always 5 minutes
    user_intent?: string;
    grade_level: string;
    
    // LEGACY FIELDS: For backward compatibility
    topic?: string;
    subject?: string;
  }): Promise<GenerationResponse> {
    const response = await apiClient.post<GenerationResponse>('/generators/lesson-starter/', {
      subject: data.subject || "Lesson Starter",
      topic: data.user_intent || data.topic || "Lesson Introduction",
      grade_level: data.grade_level,
    });
    return response.data;
  }

  async generateLearningObjectives(data: {
    // NEW CONSOLIDATED DESIGN: Single prompt with user_intent
    user_intent?: string;
    grade_level: string;
    num_objectives?: number;
    
    // LEGACY FIELDS: For backward compatibility
    topic?: string;
    subject?: string;
    number_of_objectives?: number;
    customization?: string;
  }): Promise<GenerationResponse> {
    const response = await apiClient.post<GenerationResponse>('/generators/learning-objectives/', {
      // NEW CONSOLIDATED APPROACH: Use user_intent if provided
      user_intent: data.user_intent,
      grade_level: data.grade_level,
      num_objectives: data.num_objectives || 5,
      
      // LEGACY FIELDS: Pass through for backward compatibility
      subject: data.subject,
      topic: data.topic,
      number_of_objectives: data.number_of_objectives,
      customization: data.customization,
    });
    return response.data;
  }


  async generateDiscussionQuestions(data: {
    topic: string;
    grade_level: string;
    subject?: string;
    customization?: string;
  }): Promise<GenerationResponse> {
    const response = await apiClient.post<GenerationResponse>('/generators/discussion-questions/', {
      subject: data.subject || 'Food Science',
      grade_level: data.grade_level,
      topic: data.topic,
      customization: data.customization || '',
    });
    return response.data;
  }

  async generateQuiz(data: {
    topic: string;
    grade_level: string;
    subject: string;
    number_of_questions?: number;
    question_types: string[];
  }): Promise<GenerationResponse> {
    const response = await apiClient.post<GenerationResponse>('/generators/quiz/', {
      subject: data.subject,
      grade_level: data.grade_level,
      topic: data.topic,
      number_of_questions: data.number_of_questions || 5,
      question_types: data.question_types,
    });
    return response.data;
  }

  async listGeneratedContent(params?: {
    content_type?: string;
    page?: number;
    page_size?: number;
    favorites?: boolean;
  }): Promise<GeneratedContent[]> {
    const response = await apiClient.get<any>('/generators/generated-content/', { params });
    // Handle both paginated and direct array responses
    if (Array.isArray(response.data)) {
      return response.data;
    }
    // If paginated, extract results
    if (response.data && response.data.results && Array.isArray(response.data.results)) {
      return response.data.results;
    }
    // Fallback to empty array
    return [];
  }

  async toggleFavorite(contentId: number): Promise<{ id: number; is_favorite: boolean; message: string }> {
    const response = await apiClient.post<{ id: number; is_favorite: boolean; message: string }>(
      `/generators/generated-content/${contentId}/toggle-favorite/`
    );
    return response.data;
  }

  async deleteContent(contentId: number): Promise<{ message: string; id: number }> {
    const response = await apiClient.delete<{ message: string; id: number }>(
      `/generators/generated-content/${contentId}/delete/`
    );
    return response.data;
  }
}

export const generatorService = new GeneratorService();

