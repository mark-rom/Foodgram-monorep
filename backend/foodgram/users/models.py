from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Email',
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Фамилия'
    )
    password = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Пароль'
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=['email', 'password'],
                name='unique_login_fields'
            )
        ]

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    following = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )
    sub_date = models.DateTimeField(
        'Дата подписки', auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ['-sub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_subscribtion'
            )
        ]
