from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.functions import Length, Lower

models.CharField.register_lookup(Length)
models.CharField.register_lookup(Lower)

User = get_user_model()


class Question(models.Model):
    head = models.CharField(
        verbose_name='Заголовок задания',
        max_length=150,
        blank=False
    )
    text = models.TextField(
        verbose_name='Описание задания',
        max_length=500,
        blank=False
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
            models.CheckConstraint(
                check=models.Q(head__length__gt=10),
                name='Короткий вопрос'

            ),
        )

    def __str__(self):
        return ' '.join(self.text.split()[:10])[:40]


class Answer(models.Model):
    text = models.CharField(
        verbose_name='Ответ',
        max_length=100,
        blank=False
    )
    grade = models.SmallIntegerField(
        verbose_name='Оценка за ответ',
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
        )

    def __str__(self):
        return f'{self.questions.text} {self.text}. Вес: {self.grade}'


class Result(models.Model):
    users = models.ForeignKey(
        verbose_name='Пользователь',
        related_name='results',
        to=User,
        on_delete=models.SET_DEFAULT,
        null=True,
        default=None
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
        blank=True
    )
    amount = models.SmallIntegerField(
        verbose_name='Сумма баллов',
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты'
        ordering = ('-finish_test_time',)

    def __str__(self) -> str:
        return f'Результат {self.users}: {self.amount}'
