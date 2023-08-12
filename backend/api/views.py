from django.core import exceptions
from django.db.models import Sum
from django.shortcuts import HttpResponse, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api import serializers
from api.filters import RecipesFilter
from api.pagination import CustomPaginator
from api.permissions import CustomAuthorOrReadOnly
from recipes.models import (
    Favorites,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Shopping_cart,
    Tag,
)
from users.models import Subscriptions, User


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.UserSerializer
        return serializers.UserCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        pagination_class=None,
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = serializers.UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['post'], permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = serializers.Set_PasswordSerializer(
            request.user, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        detail=True,
    )
    def subscribe(self, request, **kwargs):
        user = self.request.user
        author = get_object_or_404(User, id=kwargs['id'])
        if request.method == 'POST':
            if user == author:
                raise exceptions.ValidationError(
                    'Нет смысла подписаться на себя.'
                )
            if Subscriptions.objects.filter(user=user, author=author).exists():
                raise exceptions.ValidationError(
                    'Подписка на этого автора у вас уже есть.'
                )
            serializer = serializers.SubscriptionsSerializer(data=request.data)
            serializer.is_valid(raise_exception=False)
            Subscriptions.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(Subscriptions, user=user, author=author).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        pagination_class=CustomPaginator,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = serializers.SubscriptionsSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewsSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = [SearchFilter]
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (CustomAuthorOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipesFilter
    pagination_class = CustomPaginator
    http_method_names = ['get', 'post', 'patch', 'create', 'delete']

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return serializers.RecipeSerializer
        return serializers.RecipeCreateSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient',
            'tags',
            'favorite_recipe',
            'shopping_recipe',
        ).all()
        return recipes

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = serializers.RecipeListSerializer(
                recipe, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            if not Favorites.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                Favorites.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(
                Favorites, user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        pagination_class=None,
    )
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=kwargs['pk'])
        if request.method == 'POST':
            serializer = serializers.RecipeListSerializer(
                recipe, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            if not Shopping_cart.objects.filter(
                user=request.user, recipe=recipe
            ).exists():
                Shopping_cart.objects.create(user=request.user, recipe=recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            get_object_or_404(
                Shopping_cart, user=request.user, recipe=recipe
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, **kwargs):
        print(request)
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shopping_recipe__user=request.user
            )
            .values('ingredient')
            .annotate(total_amount=Sum('amount'))
            .values_list(
                'ingredient__name',
                'total_amount',
                'ingredient__measurement_unit',
            )
        )
        print(ingredients)
        shopping_list = []
        [
            shopping_list.append('{} - {} {}.'.format(*ingredient))
            for ingredient in ingredients
        ]
        print(shopping_list)
        response = HttpResponse(
            'Cписок покупок:\n' + '\n'.join(shopping_list),
            content_type='text/plain',
        )
        content = '\n'.join(shopping_list)
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="45.txt"'
        return response
