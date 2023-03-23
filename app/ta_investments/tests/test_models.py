from datetime import date, timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from ta_investments.models import Cashflow, Loan, User


class UserModelTests(TestCase):
    """
    Test User model.
    """

    def test_create_user_with_email_and_type_successful(self):
        """
        Test creating a User with email and type is successful.
        """
        email = "test@example.com"
        password = "testpass123"
        user_type = "Investor"
        user = User.objects.create_user(email=email, password=password, user_type=user_type)
        self.assertEqual(user.email, email)
        self.assertEqual(user.user_type, user_type)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """
        Test email is normalized for new users.
        """
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
        ]
        for email, expected in sample_emails:
            user = User.objects.create_user(email=email, password="testpass123", user_type="Investor")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raiser_error(self):
        """
        Test that creating a User without email raises value error.
        """
        with self.assertRaises(ValueError):
            User.objects.create_user("", "test123", "Investor")

    def test_create_superuser(self):
        """
        Test creating superuser.
        """
        user = User.objects.create_superuser("test@example.com", "test123", user_type="Admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_string_representation(self):
        """
        Test the string representation of the User model.
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            user_type="Investor",
        )
        self.assertEqual(str(user), user.email)
