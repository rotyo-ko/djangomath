from django.contrib import admin

from .models import Category, Exam, Question, UserTestResult, UserQuestionSelect

admin.site.register(Category)
admin.site.register(Exam)
admin.site.register(Question)
admin.site.register(UserTestResult)
admin.site.register(UserQuestionSelect)

