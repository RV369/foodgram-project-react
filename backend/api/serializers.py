import webcolors
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class UserSerializer(UserSerializer):
    """Cписок пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, validated_data):
        if (
            self.context.get('request')
            and not self.context['request'].user.is_anonymous
        ):
            return (
                self.context['request']
                .user.subscriber.filter(author=validated_data)
                .exists()
            )
        return False


class UserCreateSerializer(UserCreateSerializer):
    """Рождение пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate(self, validated_data):
        invalid_usernames = ['me']
        if self.initial_data.get('username') in invalid_usernames:
            raise serializers.ValidationError(
                {'username': 'Неподходящий username.'}
            )
        return validated_data


class Set_PasswordSerializer(serializers.Serializer):
    """Изменение пароля."""

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, validated_data):
        try:
            validate_password(validated_data['new_password'])
        except exceptions.ValidationError as exept:
            raise serializers.ValidationError(
                {'new_password': list(exept.messages)}
            )
        return super().validate(validated_data)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неправильный пароль.'}
            )
        if (
            validated_data['current_password']
            == validated_data['new_password']
        ):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего.'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class RecipeListSerializer(serializers.ModelSerializer):
    """Список рецептов."""

    image = Base64ImageField(read_only=True)
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Список авторов на которых подписан пользователь."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def get_is_subscribed(self, validated_data):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.subscriber.filter(author=validated_data).exists()
        )

    def get_recipes_count(self, validated_data):
        return validated_data.recipes.count()

    def get_recipes(self, validated_data):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = validated_data.recipes.all()
        if limit:
            recipes = recipes[: int(limit)]
        serializer = RecipeListSerializer(recipes, many=True, read_only=True)
        return serializer.data


class SubscribeListSerializer(serializers.ModelSerializer):
    """Подписка на автора и удаление подписки."""

    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeListSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )

    def validate(self, validated_data):
        if self.context['request'].user == validated_data:
            raise serializers.ValidationError(
                {'errors': 'Нет смысла подписаться на себя.'}
            )
        return validated_data

    def get_is_subscribed(self, validated_data):
        user = self.context['request'].user
        return (
            user.is_authenticated
            and user.subscriber.filter(author=validated_data).exists()
        )

    def get_recipes_count(self, validated_data):
        return validated_data.recipes.count()


class Hex2NameColor(serializers.Field):
    """Сериалайзер для поля цветов тега."""

    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для Тэгов."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер Ингредиентов."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerialiser(serializers.ModelSerializer):
    """Ингредиенты в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для Рецепта."""

    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerialiser(
        many=True, source='recipe_ingredients'
    )
    name = serializers.ReadOnlyField()
    cooking_time = serializers.ReadOnlyField()
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'image',
            'name',
            'cooking_time',
            'text',
        )

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.favorite_user.filter(recipe=obj).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        return (
            user.is_authenticated
            and user.shopping_user.filter(recipe=obj).exists()
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для Ингредиентов при создании Рецепта."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all(),
    )
    amount = serializers.IntegerField(
        max_value=settings.MAX_LIMIT, min_value=settings.MIN_LIMIT
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания Рецепта."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        max_value=settings.MAX_LIMIT, min_value=settings.MIN_LIMIT
    )

    class Meta:
        model = Recipe
        fields = (
            'name',
            'cooking_time',
            'text',
            'tags',
            'ingredients',
            'image',
            'author',
        )

    def add_ingredients(self, recipe, ingredients):
        objs = []
        for ingredient_data in ingredients:
            objs.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount'],
                )
            )
        return RecipeIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        instance = super().create(validated_data)
        self.add_ingredients(instance, ingredients)
        return instance

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.add_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
