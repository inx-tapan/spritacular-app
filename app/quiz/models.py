from django.db import models
from users.models import BaseModel, User


class QuizOption(models.Model):
    title = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = 'quiz_option'


class Question(models.Model):
    image = models.FileField(upload_to='quiz')
    correct_option = models.ManyToManyField(QuizOption)
    weightage = models.FloatField(default=1)

    def __str__(self):
        return f"{self.id}"


class Quiz(BaseModel):
    result = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.id} | Score - {self.result}"


class QuizQuestionMapping(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = 'quiz_question_mapping'


class QuizAttempt(BaseModel):
    quiz_question = models.ForeignKey(QuizQuestionMapping, on_delete=models.CASCADE)
    answer = models.ManyToManyField(QuizOption)
    question_data = models.JSONField(default=dict)
    score = models.FloatField(default=0)

    def __str__(self):
        return f"{self.id} - {self.score}"

    class Meta:
        db_table = 'quiz_attempt'


class UserQuizMapping(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} | Quiz - {self.quiz.id}"

    class Meta:
        db_table = 'user_quiz_mapping'

