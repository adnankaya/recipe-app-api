from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


class PublicIngredientsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="adnan",
            email="adnan@kayace.com",
            password="qwert1234"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_ingredients(self):
        Ingredient.objects.create(user=self.user, name="lahana")
        Ingredient.objects.create(user=self.user, name="tuz")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            username="user2",
            email="user2@kayace.com",
            password="qwert1234"
        )
        Ingredient.objects.create(user=user2, name="sirke")
        ingredient = Ingredient.objects.create(
            user=self.user, name="kestane bal")
        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        payload = {'name': 'Test ingredient'}
        self.client.post(INGREDIENTS_URL, data=payload)
        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipe(self):
        ingredient1 = Ingredient.objects.create(
            name='Breakfast', user=self.user)
        ingredient2 = Ingredient.objects.create(
            name='Breakfast', user=self.user)
        recipe = Recipe.objects.create(
            title="pizza",
            time_minutes=30,
            price=Decimal('12.22'),
            user=self.user,
        )

        recipe.ingredients.add(ingredient1)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        ingredient = Ingredient.objects.create(
            name="ingredient 1", user=self.user)
        Ingredient.objects.create(name="ingredient 2", user=self.user)
        recipe1 = Recipe.objects.create(
            title="pizza",
            time_minutes=30,
            price=Decimal('12.22'),
            user=self.user,
        )

        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title="lahmacun",
            time_minutes=60,
            price=Decimal('22.22'),
            user=self.user,
        )
        recipe2.ingredients.add(ingredient)
        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
