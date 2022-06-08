from django.contrib.auth.decorators import login_required
from django.db.models import F, Max, Q
from django.shortcuts import redirect, render

from core import utils
from core import constants as const

from .models import Answer, Question, Result, User


def index(request):
    """Обработчик для главной страницы.
    """
    grades = Answer.objects.all().values_list('grade')
    maximum = sum(grade[0] for grade in grades if grade[0] > 0)
    template = 'index.html'
    context = {
        'title': const.TITLE,
        'greeting': const.GREETING_TEXT,
        'maximum': maximum,
        'text': const.INDEX_PAGE_TEXT
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
        'title': const.TITLE,
        'header': const.ALL_RESULTS_HEADER,
        'results': results
    }

    return render(request, template, context)


@login_required
def my_results(request):
    """Показывает все результаты текущего пользователя.
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
        'title': const.TITLE,
        'header': const.MY_RESULTS_HEADER,
        'results': results
    }

    return render(request, template, context)


@login_required
def get_question(
    request, current_result=None, to_add_answer=True, error_message=None
):
    """Выводит очередной вопрос и учитывает ответы.
    Если предыдущий тест был случайно прерван, продолжит предыдущий тест.
    """
    if current_result is None:
        current_result = utils.get_current_result(request.user)

    past_question = current_result.answers.values('questions__id').last()

    if isinstance(past_question, dict):
        last_question_id = past_question.get('questions__id', 0)
    else:
        last_question_id = 0

    next_question = Question.objects.filter(id__gt=last_question_id).first()

    if not next_question:
        return to_finish_test(request, current_result)

    # Переход к обработке переданных ответов
    if request.method == 'POST' and to_add_answer:
        return add_answer(request, current_result, next_question.id)

    template = 'questions/question.html'
    context = {
        'title': const.TITLE,
        'question': next_question,
        'button_type': ('radio', 'checkbox')[next_question.many_answers],
        'error_message': error_message
    }

    return render(request, template, context)


@login_required
def add_answer(request, result, question_id):
    """Фильтрует и учитывает переданые пользователем ответы.
    """
    choice = request.POST.getlist('answer')
    if not choice:
        return get_question(
            request,
            to_add_answer=False,
            error_message=const.ERR_NO_ANSWERS
        )

    aviable_answers = Answer.objects.filter(
        Q(questions__id=question_id) &
        Q(id__in=choice)
    ).select_related('questions')

    if not aviable_answers:
        return get_question(
            request,
            to_add_answer=False,
            error_message=const.ERR_FALSE_ANSWERS
        )

    result.answers.add(*aviable_answers)

    return get_question(request, result, to_add_answer=False)


@login_required
def to_finish_test(request, result=None):
    """Завершает тест.
    Если пользователь не проходил тестов, либо пытается завершить без
    отмеченных ответов, перекидывает на главную страницу.
    Начатый тест будет продолжен в дальнейшем.
    """
    if result is None:
        result = Result.objects.filter(
            users=request.user
        ).prefetch_related(
            'answers'
        ).order_by('-id').first()

    if result is None or not result.answers.all():
        return redirect('questions:index')

    if not result.finish_test_time:
        utils.close_last_result(result)

    if result.amount < 0:
        return redirect(const.LOSE)

    template = 'questions/finish.html'
    context = {
        'title': const.TITLE,
        'header': const.FINISH_HEADER,
        'result': result
    }
    return render(request, template, context)
