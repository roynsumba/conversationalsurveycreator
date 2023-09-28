from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser, Survey, SurveyResponse, AuthorizedEmail
from .models import CustomUser

class CustomUserCreationTestCase(TestCase):
    
    def test_custom_user_creation(self):
        # Test normal user creation using CustomUserManager
        user = CustomUser.objects.create_user(
            email='testuser@example.com', 
            name='Test User', 
            password='testpassword123',
            is_surveycreator=True
        )

        self.assertEqual(user.email, 'testuser@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.check_password('testpassword123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_surveycreator)

    def test_create_user_without_email(self):
        # Test user creation without an email
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email='', name='No Email User')

    def test_default_values_for_new_user(self):
        # Test that default values are set correctly
        user = CustomUser.objects.create_user(
            email='defaulttest@example.com', 
            name='Default User', 
            password='defaultpassword123'
        )
        
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_surveycreator)


