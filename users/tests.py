from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from .models import CustomUser

class UserAuthenticationTests(TestCase):

    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'password1': 'password123',
            'password2': 'password123',
        }
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            password='password123'
        )
        self.login_url = reverse('login')
        self.dashboard_url = reverse('dashboard')

        # Create the necessary groups
        self.default_group = Group.objects.create(name='Default')
        self.staff_group = Group.objects.create(name='Staff')
        self.superuser_group = Group.objects.create(name='Superuser')

    def test_user_can_register(self):
        response = self.client.post(reverse('register'), data=self.user_data, follow=True)
        print(response.content)  # Print the response content for debugging
        print(response.status_code)  # Print the response status code for debugging
        self.assertEqual(response.status_code, 302)  # Expect a redirect after successful registration
        self.assertRedirects(response, self.login_url)  # Verify that the user is redirected to the login page

    def test_user_can_login(self):
        response = self.client.post(self.login_url, data={'email': self.user_data['email'], 'password': self.user_data['password1']}, follow=True)
        print(response.content)  # Print the response content for debugging
        print(response.status_code)  # Print the response status code for debugging
        self.assertEqual(response.status_code, 302)  # Expect a redirect after successful login
        self.assertRedirects(response, self.dashboard_url)  # Verify that the user is redirected to the dashboard

    def test_user_can_access_dashboard(self):
        self.client.login(email=self.user_data['email'], password=self.user_data['password1'])
        response = self.client.get(self.dashboard_url)
        print(response.content)  # Print the response content for debugging
        print(response.status_code)  # Print the response status code for debugging
        self.assertEqual(response.status_code, 200)  # Expect a successful access to the dashboard

    def test_user_can_logout(self):
        self.client.login(email=self.user_data['email'], password=self.user_data['password1'])
        response = self.client.get(reverse('logout'), follow=True)
        print(response.content)  # Print the response content for debugging
        print(response.status_code)  # Print the response status code for debugging
        self.assertEqual(response.status_code, 302)  # Expect a redirect after successful logout
        self.assertRedirects(response, self.login_url)  # Verify that the user is redirected to the login page

    def test_user_is_assigned_to_default_group(self):
        self.assertTrue(self.user.groups.filter(name=self.default_group.name).exists())

    def test_user_is_not_assigned_to_staff_group(self):
        self.assertFalse(self.user.groups.filter(name=self.staff_group.name).exists())

    def test_user_is_not_assigned_to_superuser_group(self):
        self.assertFalse(self.user.groups.filter(name=self.superuser_group.name).exists())
