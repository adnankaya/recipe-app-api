from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Tests the user api public"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successfull(self):
        """Test creating user with payload(the object you request) 
        is successful"""
        payload = {
            "username": "adnan",
            "email": "adnan@kayace.com",
            "password": "qwert12345"
        }
        res = self.client.post(CREATE_USER_URL, data=payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        payload = {
            "username": "adnan",
            "email": "adnan@kayace.com",
            "password": "qwert12345"
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        payload = {
            "username": "adnan",
            "email": "adnan@kayace.com",
            "password": "qw"
        }
        res = self.client.post(CREATE_USER_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_user_for_token(self):
        payload = {
            "username": "adnan",
            "email": "adnan@kayace.com",
            "password": "qwert12345"
        }
        create_user(**payload)
        res = self.client.post(TOKEN_URL, data=payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        create_user(username='adnan',
                    email='adnan@kayace.com',
                    password='deneme1234')
        payload = {
            "username": "adnan",
            "email": "adnan@kayace.com",
            "password": "qwert12345"
        }
        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        payload = {
            "username": "adnan",
            "email": "adnan@kayace.com",
            "password": "qwert12345"
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_data(self):
        res = self.client.post(
            TOKEN_URL, {'username': "ad", 'email': 'adnan', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
