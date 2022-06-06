from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Length, Lower

models.CharField.register_lookup(Length)
models.CharField.register_lookup(Lower)

User = get_user_model()


class Question(models.Model):
    text = models.CharField(
        verbose_name='Вопрос',
        max_length=300,
        null=False
    )
    many_answers = models.BooleanField(
        verbose_name='Несколько правильных ответов',
        null=False,
        default=False
    )

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        constraints = (
            models.UniqueConstraint(
                Lower('text'),
                name='Не уникальный вопрос'
            ),
            models.CheckConstraint(
                check=models.Q(text__length__gt=0),
                name='Короткткий вопрос'

            )
        )

    def __str__(self):
        return ' '.join(self.text.split()[:4])[:40]


class Answer(models.Model):
    text = models.CharField(
        verbose_name='Ответ',
        max_length=100,
        null=False
    )
    weight = models.PositiveSmallIntegerField(
        verbose_name='Вес ответа',
        null=False,
        default=0
    )
    questions = models.ForeignKey(
        verbose_name='Вопрос к этому ответу',
        related_name='answers',
        to=Question,
        on_delete=models.CASCADE,
        null=False
    )

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        constraints = (
            models.UniqueConstraint(
                fields=('text', 'questions'),
                name='Одинаковые ответы у вопроса'
            ),
            models.CheckConstraint(
                check=models.Q(text__length__gt=0),
                name='Пустой ответ'
            )
        )

    def __str__(self):
        return f'{self.questions.text} {self.text}. Вес: {self.weight}'


class Result(models.Model):
    users = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='results',
        to=User,
        on_delete=models.SET_DEFAULT,
        default=None,
        null=True
    )
    answers = models.ManyToManyField(
        verbose_name='Выбранные ответы',
        related_name='results',
        to=Answer
    )
    start_test_time = models.DateTimeField(
        verbose_name='Время начала теста',
        null=False,
        auto_now_add=True
    )
    finish_test_time = models.DateTimeField(
        verbose_name='Время завершения теста',
        null=True,
    )
    amount = models.SmallIntegerField(
        verbose_name='Сумма баллов',
        null=False,
        default=0
    )

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'
        ordering = ('-finish_test_time',)

    def __str__(self) -> str:
        return f'Результат {self.user}: {self.amount}'
