from django.contrib.auth.models import AbstractUser
from django.db import models

from recipes.models import Recipe


class User(AbstractUser):
    """
    Модель для описания пользователей.
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
    password = models.CharField(
        'Пароль',
        max_length=150,
    )
    subscribing = models.ManyToManyField(
        to='self',
        through='Subscribe',
        symmetrical=False,
        verbose_name='Подписчики',
    )
    favorite_recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Избранные рецепты',
        related_name='favorites',
    )
    shopping_recipes = models.ManyToManyField(
        Recipe,
        verbose_name='Рецепты в списке покупок',
        related_name='shoppings',
    )

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = [
        'username',
        'first_name',
        'last_name',
        'password',
    ]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='уникальность пары имя пользователя-адрес email',
            ),
        ]

    def __str__(self):
        return f'{self.username}'


class Subscribe(models.Model):
    """
    Модель для описания системы подписки.
    """

    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='subscriber',
    )
    user_author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='author',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'user_author'],
                name='уникальность пары подписчик-автор',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('user_author')),
                name='запрет подписки на самого себя',
            ),
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.user_author}'
