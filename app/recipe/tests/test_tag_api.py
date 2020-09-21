from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer


TAGS_URL = reverse("recipe:tag-list")


class PublicTagsApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="adnan",
            email="adnan@kayace.com",
            password="qwert1234"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_tags(self):
        Tag.objects.create(user=self.user, name="vegan")
        Tag.objects.create(user=self.user, name="desert")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            username="user2",
            email="user2@kayace.com",
            password="qwert1234"
        )
        Tag.objects.create(user=user2, name="fruity")
        tag = Tag.objects.create(user=self.user, name="comfort food")
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        payload = {'name': 'Test tag'}
        self.client.post(TAGS_URL, data=payload)
        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        tag1 = Tag.objects.create(name='Breakfast', user=self.user)
        tag2 = Tag.objects.create(name='Breakfast', user=self.user)
        recipe = Recipe.objects.create(
            title="pizza",
            time_minutes=30,
            price=Decimal('12.22'),
            user=self.user,
        )

        recipe.tags.add(tag1)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        tag = Tag.objects.create(name="tag 1", user=self.user)
        Tag.objects.create(name="tag 2", user=self.user)
        recipe1 = Recipe.objects.create(
            title="pizza",
            time_minutes=30,
            price=Decimal('12.22'),
            user=self.user,
        )

        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title="lahmacun",
            time_minutes=60,
            price=Decimal('22.22'),
            user=self.user,
        )
        recipe2.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
