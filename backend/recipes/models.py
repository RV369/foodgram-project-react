from django.core.validators import MinValueValidator, RegexValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    name = models.CharField(max_length=200)
    color = models.CharField(
        verbose_name='Код цвета',
        max_length=7,
        null=True,
        validators=[
            RegexValidator(
                '^#([a-fA-F0-9]{6})',
                message='Пропишите в поле код выбранного цвета.',
            )
        ],
    )
    slug = models.SlugField(unique=True, max_length=200)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200)
    measurement_unit = models.CharField(max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    tags = models.ManyToManyField(Tag)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(
        upload_to='recipes/images/', null=True, blank=True, default=None
    )
    name = models.CharField(max_length=200)
    text = models.TextField(
        max_length=200, null=True, blank=True, default=None
    )
    cooking_time = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1)]
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'),
    )
    pub_date = models.DateTimeField(
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
        Recipe, related_name='recipe_ingredients', on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveBigIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        verbose_name = 'Ингредиенты для приготовления рецепта'
        verbose_name_plural = 'Ингредиенты для рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'], name='unique_combination'
            )
        ]

    def __str__(self):
        return f'{self.recipe.name}: ' f'{self.ingredient.name} - '


class Shopping_cart(models.Model):
    Ingredients = models.ManyToManyField(Ingredient, blank=True)
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
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'
