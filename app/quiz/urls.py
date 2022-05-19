from django.urls import path
from .views import GetQuizQuestionsViewSet, QuizViewSet

urlpatterns = [
    # Get quiz questions
    path('get_quiz_questions/', GetQuizQuestionsViewSet.as_view(), name='get_quiz_questions'),
    path('submit/', QuizViewSet.as_view({'post': 'create'}), name='submit'),
]
