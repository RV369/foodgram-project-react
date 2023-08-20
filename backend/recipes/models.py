from django.conf import settings
from django.core import validators
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(verbose_name='Тег', max_length=settings.MAX_LENGTH)
    color = models.CharField(
        verbose_name='Код цвета тега',
        max_length=7,
        null=True,
        validators=[
            validators.RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Пропишите в поле код выбранного цвета.',
            )
        ],
    )
    slug = models.SlugField(
        verbose_name='Слаг тега', unique=True, max_length=settings.MAX_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Ингредиент', max_length=settings.MAX_LENGTH
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения', max_length=settings.MAX_LENGTH
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag, verbose_name='Тег рецепта')
    author = models.ForeignKey(
        User, verbose_name='Автор рецепта', on_delete=models.CASCADE
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        blank=True,
        default=None,
        verbose_name='Фотография готового блюда',
    )
    name = models.CharField(
        max_length=settings.MAX_LENGTH, verbose_name='Наименование рецепта'
    )
    text = models.TextField(
        max_length=settings.MAX_LENGTH,
        null=True,
        blank=True,
        default=None,
        verbose_name='Рецепт',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления блюда',
        validators=[
            validators.MinValueValidator(settings.MIN_LIMIT),
            validators.MaxValueValidator(settings.MAX_LIMIT),
        ],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты в рецепте',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации рецепта',
        auto_now_add=True,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        related_name='recipe_ingredients',
        on_delete=models.CASCADE,
        verbose_name='Набор ингредиентов в рецепте',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиенты в рецепте',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            validators.MinValueValidator(settings.MIN_LIMIT),
            validators.MaxValueValidator(settings.MAX_LIMIT),
        ],
    )

    class Meta:
        ordering = ['recipe']
        verbose_name = 'Ингредиенты для приготовления рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique_combination'
            )
        ]

    def __str__(self):
        return (
            f'{self.recipe.name}: '
            f'{self.ingredient.name} - '
            f'{self.amount} '
            f'{self.ingredient.measurement_unit}'
        )


class Shopping_cart(models.Model):
    Ingredients = models.ManyToManyField(
        Ingredient, verbose_name='Ингредиент в кщрзине', blank=True
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_user',
        verbose_name='Покупатель',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_recipe',
        verbose_name='Рецепт в корзине',
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины покупок пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class Favorites(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_user',
        verbose_name='В избранном у пользователя',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт',
    )

    class Meta:
        ordering = ['user']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
