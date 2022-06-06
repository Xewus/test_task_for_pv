from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.db.models import Max, F, Q

from .models import Question, Answer, User, Results
from core import utils
from . import forms

TITLE = ' Проверь своего Питона'

# class QuestionView(CreateView):
#     form_class = QuestionForm
#     te


def index(request):
    """Обработчик для главной страницы.
    """
    template = 'index.html'
    context = {
        'title': TITLE,
        'text': 'Готовы к проверке знаний?'
    }
    return render(request, template, context)


def all_results(request):
    """Показывает рейтинг.
    """
    results = User.objects.values(
        'username'
    ).annotate(
        amount=Max('results__amount')
    ).order_by('-amount')
    template = 'questions/results.html'
    context = {
        'title': TITLE,
        'header': 'Рейтинг участников',
        'results': results
    }

    return render(request, template, context)


@login_required
def my_results(request):
    """Показывает результаты текущего пользователя.
    """
    results = User.objects.filter(
        id=request.user.id
        ).values(
            'username',
            amount=F('results__amount'),
            finish_test_time=F('results__finish_test_time')
        ).order_by(
            '-results__finish_test_time')

    template = 'questions/results.html'
    context = {
        'title': TITLE,
        'header': 'История Ваших тестов',
        'results': results
    }

    return render(request, template, context)


@login_required
def get_question(request, current_result=None, error_message=None):
    """Выводит очередной вопрос.
    Если предыдущий тест был случайно прерван, продолжит предыдущий тест.
    """
    if current_result is None:
        current_result = utils.get_current_result(request.user)

    past_question = current_result.answers.values('question__id').last()

    if isinstance(past_question, dict):
        last_question_id = past_question.get('question__id', 0)
    else:
        last_question_id = 0

    next_question = Question.objects.filter(id__gt=last_question_id).first()

    if not next_question:
        utils.close_last_result(current_result)
        return redirect('questions:finish_test')

    if request.method == 'POST':
        return add_answer(request, current_result, next_question.id)

    template = 'questions/question.html'
    context = {
        'title': TITLE,
        'header': 'Ответьте на вопрос ниже',
        'question': next_question,
        'button_type': ('radio', 'checkbox')[next_question.many_answers],
        'error_message': error_message
    }

    return render(request, template, context)


@login_required
def add_answer(request, result, question_id):
    """Учитывает выбранный пользователем ответ.
    """
    choice = request.POST.getlist('answer')
    request.method = 'GET'
    if not choice:
        return get_question(
            request, error_message='Вы не выбрали ответ.'
        )

    on_question = Q(question__id=question_id)
    answers_in_choice = Q(id__in=choice)

    aviable_answers = Answer.objects.filter(
        on_question & answers_in_choice
    ).select_related('question')

    if not aviable_answers:
        return get_question(
            request, error_message='Повторите выбор.'
        )

    result.answers.add(*aviable_answers)

    return get_question(request, result)


@login_required
def to_finish_test(request):
    """Завершает тест.
    """
    result = Results.objects.filter(user=request.user).prefetch_related('answers').order_by('-id').first()
    if result is None or not result.answers.all():
        return redirect('questions:index')

    if not result.finish_test_time:
        utils.close_last_result(result)

    template = 'questions/finish.html'
    context = {
        'title': TITLE,
        'header': 'За сим всё',
        'result': result
    }
    return render(request, template, context)
