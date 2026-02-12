from django.urls import path
from .views import (
    GeneratedContentView,
    ToggleFavoriteView,
    DeleteContentView,
    LessonStarterGenerateView,
    LearningObjectivesGenerateView,
    DiscussionQuestionsGenerateView,
    QuizGenerateView,
    DocumentExportView
)

app_name = 'generators'

urlpatterns = [
    path('generated-content/', GeneratedContentView.as_view(), name='generated-content'),
    path('generated-content/<int:content_id>/toggle-favorite/', ToggleFavoriteView.as_view(), name='toggle-favorite'),
    path('generated-content/<int:content_id>/delete/', DeleteContentView.as_view(), name='delete-content'),
    path('lesson-starter/', LessonStarterGenerateView.as_view(), name='lesson-starter-generate'),
    path('learning-objectives/', LearningObjectivesGenerateView.as_view(), name='learning-objectives-generate'),
    path('discussion-questions/', DiscussionQuestionsGenerateView.as_view(), name='discussion-questions-generate'),

    path('quiz/', QuizGenerateView.as_view(), name='quiz-generate'),
    path('<int:content_id>/export/<str:format_type>/', DocumentExportView.as_view(), name='document-export'),
]