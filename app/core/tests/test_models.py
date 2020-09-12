from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Testing user creation """
        username = "adnan"
        email = "adnan@kayace.com"
        password = "deneme1234"
        user = get_user_model().objects.create_user(
            username,
            email,
            password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        email = "adnan@KAYACE.COM"
        username = "adnan"
        password = "deneme1234"
        user = get_user_model().objects.create_user(
            username,
            email,
            password
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("adnan", None, 'deneme1234')

    def test_create_new_super_user(self):
        user = get_user_model().objects.create_superuser(
            username='adnan',
            email="adnan@kayace.com",
            password="deneme1234"
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
