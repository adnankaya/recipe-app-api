from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username='adnan',
            email='adnan@kayace.com',
            password="deneme1234"
        )
        self.client.force_login(self.admin_user)
        self.test_user = get_user_model().objects.create_user(
            username='testuser',
            email='test@kayace.com',
            password="deneme1234"
        )

    def test_users_listed(self):
        # https://docs.djangoproject.com/en/2.1/ref/contrib/admin/#django.contrib.admin.ModelAdmin.changelist_view
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.test_user.email)
        self.assertContains(res, self.test_user.get_full_name())

    def test_user_change_page(self):
        """Test user edit page"""
        url = reverse('admin:core_user_change', args=[self.test_user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)
