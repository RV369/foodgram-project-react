# Generated by Django 3.2 on 2023-08-13 20:20

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorites',
            options={
                'ordering': ['user'],
                'verbose_name': 'Избранное',
                'verbose_name_plural': 'Избранное',
            },
        ),
        migrations.AlterModelOptions(
            name='recipeingredient',
            options={
                'ordering': ['recipe'],
                'verbose_name': 'Ингредиенты для приготовления рецепта',
                'verbose_name_plural': 'Ингредиенты для рецептов',
            },
        ),
        migrations.AlterModelOptions(
            name='shopping_cart',
            options={
                'ordering': ['user'],
                'verbose_name': 'Корзина',
                'verbose_name_plural': 'Корзины покупок пользователей',
            },
        ),
        migrations.AlterModelOptions(
            name='tag',
            options={
                'ordering': ['name'],
                'verbose_name': 'Тег',
                'verbose_name_plural': 'Теги',
            },
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(
                max_length=200, verbose_name='Единица измерения'
            ),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Ингредиент'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to=settings.AUTH_USER_MODEL,
                verbose_name='Автор рецепта',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(32000),
                ],
                verbose_name='Время приготовления блюда',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(
                blank=True,
                default=None,
                null=True,
                upload_to='recipes/images/',
                verbose_name='Фотография готового блюда',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(
                through='recipes.RecipeIngredient',
                to='recipes.Ingredient',
                verbose_name='Ингредиенты в рецепте',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(
                max_length=200, verbose_name='Наименование рецепта'
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='pub_date',
            field=models.DateTimeField(
                auto_now_add=True,
                null=True,
                verbose_name='Дата публикации рецепта',
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(
                to='recipes.Tag', verbose_name='Тег рецепта'
            ),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='text',
            field=models.TextField(
                blank=True,
                default=None,
                max_length=200,
                null=True,
                verbose_name='Рецепт',
            ),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='amount',
            field=models.PositiveSmallIntegerField(
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(32000),
                ],
                verbose_name='Количество',
            ),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='ingredient',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='recipes.ingredient',
                verbose_name='Ингредиенты в рецепте',
            ),
        ),
        migrations.AlterField(
            model_name='recipeingredient',
            name='recipe',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='recipe_ingredients',
                to='recipes.recipe',
                verbose_name='Набор ингредиентов в рецепте',
            ),
        ),
        migrations.AlterField(
            model_name='shopping_cart',
            name='Ingredients',
            field=models.ManyToManyField(
                blank=True,
                to='recipes.Ingredient',
                verbose_name='Ингредиент в кщрзине',
            ),
        ),
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=models.CharField(
                max_length=7,
                null=True,
                validators=[
                    django.core.validators.RegexValidator(
                        '^#([a-fA-F0-9]{6})',
                        message='Пропишите в поле код выбранного цвета.',
                    )
                ],
                verbose_name='Код цвета тега',
            ),
        ),
        migrations.AlterField(
            model_name='tag',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Тег'),
        ),
        migrations.AlterField(
            model_name='tag',
            name='slug',
            field=models.SlugField(
                max_length=200, unique=True, verbose_name='Слаг тега'
            ),
        ),
    ]
