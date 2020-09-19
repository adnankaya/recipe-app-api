from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from core.models import Tag
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
