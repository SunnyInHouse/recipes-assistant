from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Модель для описания пользователей.
    """

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        error_messages={
            'unique': 'Пользователь с указанным username уже существует.',
        }
    )
    first_name = models.CharField(
        'Имя пользователя',
        max_length=150,
    )
    last_name = models.CharField(
        'Фамилия пользователя',
        max_length=150,
    )
    email = models.EmailField(
        'Адрес e-mail',
        max_length=254,
        unique=True,
        error_messages={
            'unique': 'Пользователь с указанным e-mail уже существует.',
        }

    )

    REQUIRED_FIELDS = [
        'first_name',
        'last_name',
        'email',
        'password',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return f'{self.username}'


class Subscribe(models.Model):
    """Модель для описания системы подписки.
    """
    user_subscriber = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscribers',
    )
    user_author = models.ForeignKey(
        User,
        verbose_name='Автор, на которого подписывается подписчик',
        on_delete=models.CASCADE,
        related_name='authors',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user_subscriber',)
        constraints = [
            models.UniqueConstraint(
                fields=['user_subscriber', 'user_author'],
                name='уникальность пары подписчик-автор',
            ),
            models.CheckConstraint(
                check=~models.Q(user_subscriber=models.F('user_author')),
                name='запрет подписки на самого себя',
            ),
        ]

    def __str__(self):
        return f'{self.user_subscriber} подписан на {self.user_author}'
