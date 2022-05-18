from django.urls import path
from .views import GetQuizQuestionsViewSet

urlpatterns = [
    # Get quiz questions
    path('get_quiz_questions/', GetQuizQuestionsViewSet.as_view(), name='get_quiz_questions'),
]
