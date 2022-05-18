from django.contrib import admin
from .models import QuizOption, Question, Quiz, QuizAttempt, QuizQuestionMapping, UserQuizMapping

admin.site.register(QuizOption)
admin.site.register(Question)
admin.site.register(Quiz)
admin.site.register(QuizAttempt)
admin.site.register(QuizQuestionMapping)
admin.site.register(UserQuizMapping)
