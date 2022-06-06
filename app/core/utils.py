from datetime import datetime
from django.db.models import Q, Sum
from questions.models import Results


def get_last_open_result(user):
    """Ищет отрытый тест."""
    current_user = Q(user=user)
    not_finished = Q(finish_test_time=None)
    return Results.objects.filter(
        current_user & not_finished
    ).select_related('user').last()


def get_current_result(user):
    result = get_last_open_result(user)
    if not result:
        result = Results.objects.create(user=user)
    return result


def close_last_result(result):
    """Закрывает тест с указанием времни закрытия.
    """
    amount = result.answers.aggregate(Sum('weight'))['weight__sum']
    if amount is None:
        amount = 0
    result.amount = amount
    result.finish_test_time = datetime.now()
    result.save()
    return
