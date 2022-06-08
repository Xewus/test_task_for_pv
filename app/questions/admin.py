from django import forms
from django.contrib import admin

from .models import Answer, Question, Result


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'text', 'grade', 'questions'
    )
    search_fields = (
        'text', 'questions__text', 'questions__head'
    )
    list_filter = (
        'questions__head',
    )


@admin.register(Result)
class ResultsAdmin(admin.ModelAdmin):
    list_display = (
        'users',
        'amount',
        'finish_test_time'
    )
    search_fields = (
        'users__username',
    )
    list_filter = (
        'finish_test_time',
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    # def get_form(self, request, obj=None, **kwargs):
    #     kwargs['widgets'] = {'text': forms.Textarea}
    #     return super().get_form(request, obj, **kwargs)

    list_display = (
        'id',
        'text',
        'many_answers',
        'get_max_points'
    )
    inlines = (AnswerInline,)

    search_fields = (
        'text',
        'answers__text'
    )

    list_filter = (
         'many_answers',
    )

    def get_max_points(self, question):
        grades = question.answers.all().values_list('grade')
        return sum(grade[0] for grade in grades if grade[0] > 0)
