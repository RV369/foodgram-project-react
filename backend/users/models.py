from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(max_length=settings.LEN_EMAIL, unique=True)
    username = models.CharField(max_length=settings.LEN_STRING, unique=True)
    first_name = models.CharField(
        'имя', max_length=settings.LEN_STRING, blank=True
    )
    last_name = models.CharField(
        'фамилия', max_length=settings.LEN_STRING, blank=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscriber',
        verbose_name='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribing',
        verbose_name='Автор рецепта',
    )
    date_subscriptions = models.DateTimeField(
        editable=False, auto_now_add=True
    )

    class Meta:
        ordering = ['-date_subscriptions']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки пользователей'

    def __str__(self):
        return f'{self.user.username} - {self.author.username}'
