import random

from django.db.models import Sum, Count, Q
from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from sentry_sdk import capture_exception

from users.models import User
from .models import QuizOption, Question, Quiz, QuizQuestionMapping, QuizAttempt, UserQuizMapping, Configuration
from .serializers import QuizSerializer, QuizQuestionMappingSerializer, QuizAttemptSerializer, UserQuizMappingSerializer


def get_total_quiz_questions():
    config_obj = Configuration.objects.filter(key='TOTAL_QUIZ_QUESTIONS').last()
    total_questions = 15
    if config_obj:
        total_questions = config_obj.value.get('total_quiz_questions')

    return total_questions


class GetQuizQuestionsViewSet(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        question_list = list(Question.objects.all())
        total_questions = get_total_quiz_questions()
        random_question_list = random.sample(question_list, total_questions)

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
                'id': q_opt.id,
                'title': q_opt.title.title()
            }

            option_data.append(option_record)

        return Response({'question_list': question_data,
                         'option_list': option_data},
                        status=status.HTTP_200_OK)


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = QuizSerializer

    @staticmethod
    def check_answer(question_id, ans_list):
        question_obj = Question.objects.get(id=question_id)
        correct_ans = list(question_obj.correct_option.filter().values_list('id', flat=True))
        for i in ans_list:
            if not question_obj.correct_option.filter(id=i).exists():
                return 0, correct_ans
        return 1, correct_ans

    def create(self, request, *args, **kwargs):
        data = request.data
        total_questions = get_total_quiz_questions()
        # data = [
        #     {
        #         "que": 2,
        #         "ans": [1]
        #     },
        #     {
        #         "que": 3,
        #         "ans": [3, 4]
        #     },
        #     {
        #         "que": 30,
        #         "ans": [1]
        #     }
        # ]
        error_message = None
        # answers = data.get('answers')
        if len(data) != total_questions:
            return Response({'details': '15 questions not available.', 'status': 0}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                serializer = self.serializer_class(data={'result': {}})
                serializer.is_valid(raise_exception=True)
                quiz_obj = serializer.save()
                print("QUIZ CREATED")

                for ques in data:
                    serializer = QuizQuestionMappingSerializer(data={'quiz': quiz_obj.id,
                                                                     'question': ques.get('que')})
                    serializer.is_valid(raise_exception=True)
                    quiz_question_obj = serializer.save()
                    # ques_ans = answers[i]
                    ques_ans = ques.get('ans')
                    if not ques_ans:
                        error_message = f"No option selected for question => {ques.get('que')}"
                        raise ValidationError()

                    # Check if the answers are correct or incorrect.
                    score, correct_ans = self.check_answer(ques.get('que'), ques_ans)
                    quiz_attempt = QuizAttemptSerializer(data={'quiz_question': quiz_question_obj.id,
                                                               'answer': ques.get('ans'),
                                                               'score': score,
                                                               'question_data': {"correct_ans": correct_ans}})

                    quiz_attempt.is_valid(raise_exception=True)
                    quiz_attempt.save()

                serializer = UserQuizMappingSerializer(data={'user': request.user.id, 'quiz': quiz_obj.id})
                serializer.is_valid(raise_exception=True)
                serializer.save()
                print("**** Success!! ****")

                aggregate_score = QuizAttempt.objects.filter(quiz_question__quiz=quiz_obj)\
                    .aggregate(total_score=Sum('score'), correct_answers=Count('score', filter=Q(score=1.0)))

                get_final_result = (aggregate_score.get('total_score')/total_questions) * 100
                if get_final_result > 75:
                    # Making user trained
                    user_obj = User.objects.get(id=request.user.id)
                    user_obj.is_trained = True
                    user_obj.save(update_fields=['is_trained'])

                quiz_obj.result = {'percentage': get_final_result}
                quiz_obj.save()

            return Response({'success': 'Quiz submitted successfully', 'score': get_final_result,
                             'correct_answers': aggregate_score.get('correct_answers'), 'status': 1},
                            status=status.HTTP_201_CREATED)

        except ValidationError as e:
            capture_exception(e)
            print(f"GOT IT----{e}")

        return Response({'errors': serializer.errors or error_message}, status=status.HTTP_400_BAD_REQUEST)


