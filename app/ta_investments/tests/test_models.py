from decimal import Decimal
from django.test import TestCase
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from ta_investments.models import Loan, Cashflow, User


class UserModelTests(TestCase):
    """
    Test User model.
    """

    def test_create_user_with_email_successful(self):
        """
        Test creating a User with email is successful.
        """
        email = "test@example.com"
        password = "testpass123"
        user = User.objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test email is normalized for new users.
        """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
        ]
        for email, expected in sample_emails:
            user = User.objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raiser_error(self):
        """
        Test that creating a User without email raises value error.
        """
        with self.assertRaises(ValueError):
            User.objects.create_user("", "test123")

    def test_create_superuser(self):
        """
        Test creating superuser.
        """
        user = User.objects.create_superuser(
            'test@example.com',
            'test123',
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

