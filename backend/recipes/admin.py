from django.contrib import admin

from recipes import models


class RecipesIngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'in_favorites')
    list_editable = ('name', 'author')
    readonly_fields = ('in_favorites',)
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'
    inlines = (RecipesIngredientInline,)

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorite_recipe.count()


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(models.Favorites)
class FavoritesAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')


@admin.register(models.Shopping_cart)
class Shopping_CartAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'recipe')
    list_editable = ('user', 'recipe')
