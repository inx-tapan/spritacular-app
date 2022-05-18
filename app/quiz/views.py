import random

from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import QuizOption, Question, Quiz, QuizQuestionMapping, QuizAttempt, UserQuizMapping


class GetQuizQuestionsViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        question_list = list(Question.objects.all())
        random_question_list = random.sample(question_list, 15)

        question_data = []
        for i in random_question_list:
            record = {
                'id': i.id,
                'image_url': i.image.url,
            }

            question_data.append(record)

        option_data = []
        for q_opt in QuizOption.objects.all():
            option_record = {
                'title': q_opt.title
            }

            option_data.append(option_record)

        return Response({'question_list': question_data,
                         'option_list': option_data},
                        status=status.HTTP_200_OK)

