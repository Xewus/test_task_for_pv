from datetime import datetime

from django.db.models import Q, Sum
from django.shortcuts import redirect

from questions.models import Result


def get_last_open_result(user):
    """Ищет отрытый тест.
    """
    return Result.objects.filter(
        Q(users=user) & Q(finish_test_time=None)
    ).select_related('users').last()


def get_current_result(user):
    """Получает последний незакрый тест либо создаёт новыйю
    """
    result = get_last_open_result(user)
    if not result:
        result = Result.objects.create(users=user)
    return result


def close_last_result(result):
    """Закрывает тест с указанием времни закрытия и
    проставлением суммы набранных баллов.
    """
    amount = result.answers.aggregate(Sum('grade'))['grade__sum']
    if amount is None:
        amount = 0
    result.amount = amount
    result.finish_test_time = datetime.now()
    result.save()
    return

