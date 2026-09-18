from django.test import TestCase
from django.urls import reverse

class AccountsAccessibilityTest(TestCase):
    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    def test_register_page_loads(self):
        response = self.client.get(reverse('registerUser'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
