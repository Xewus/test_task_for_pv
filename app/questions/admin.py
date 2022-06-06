from django.contrib import admin
from django.db.models import Sum, Max

from .models import Question, Answer, Result


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 2

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        'text', 'weight', 'questions'
    )
    search_fields = (
        'text', 'questions__text'
    )
    list_filter = (
        'questions',
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
    list_display = (
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
        if question.many_answers:
            return question.answers.aggregate(Sum('weight'))['weight__sum']
        return question.answers.aggregate(Max('weight'))['weight__max']
