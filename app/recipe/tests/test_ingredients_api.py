from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from core.models import Ingredient
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
