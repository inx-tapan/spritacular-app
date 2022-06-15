from rest_framework.serializers import ModelSerializer

from .models import QuizOption, Question, Quiz, QuizQuestionMapping, QuizAttempt, UserQuizMapping


class QuizOptionSerializer(ModelSerializer):

    class Meta:
        model = QuizOption
        fields = '__all__'


class QuestionSerializer(ModelSerializer):

    class Meta:
        model = Question
        fields = '__all__'


class QuizSerializer(ModelSerializer):

    class Meta:
        model = Quiz
        fields = '__all__'


class QuizQuestionMappingSerializer(ModelSerializer):

    class Meta:
        model = QuizQuestionMapping
        fields = '__all__'


class QuizAttemptSerializer(ModelSerializer):

    class Meta:
        model = QuizAttempt
        fields = '__all__'


class UserQuizMappingSerializer(ModelSerializer):

    class Meta:
        model = UserQuizMapping
        fields = '__all__'


# class TestQuizSerializer(ModelSerializer):
#     quiz_question = QuizQuestionMappingSerializer(read_only=True, many=True)
#     quiz_attempt = QuizAttemptSerializer(read_only=True, many=True)
#     user_quiz = UserQuizMappingSerializer(read_only=True)
#
#     class Meta:
#         model = Quiz
#         fields = ('quiz_question', 'quiz_attempt', 'user_quiz')







