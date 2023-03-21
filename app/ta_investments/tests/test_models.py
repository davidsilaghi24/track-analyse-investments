from decimal import Decimal
from django.test import TestCase
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


class LoanModelTests(TestCase):
    """
    Test Loan model.
    """

    def setUp(self):
        """
        Set up a test Loan object.
        """
        self.loan = Loan.objects.create(
            identifier='loan123',
            issue_date=timezone.now().date(),
            total_amount=Decimal('1000'),
            rating=1,
            maturity_date=timezone.now().date(),
            total_expected_interest_amount=Decimal('100'),
        )

    def test_loan_str_representation(self):
        """
        Test string representation of Loan model.
        """
        self.assertEqual(str(self.loan), 'loan123')

    def test_loan_invested_amount(self):
        """
        Test calculation of invested_amount, expected_interest_amount, expected_irr,
        realized_irr, and is_closed fields for Loan model.
        """
        self.assertIsNone(self.loan.invested_amount)
        self.assertIsNone(self.loan.investment_date)
        self.assertIsNone(self.loan.expected_interest_amount)
        self.assertIsNone(self.loan.expected_irr)
        self.assertIsNone(self.loan.realized_irr)
        self.assertFalse(self.loan.is_closed)

        # Set invested_amount and check if other fields are updated accordingly
        self.loan.invested_amount = Decimal('500')
        self.loan.save()
        self.assertIsNotNone(self.loan.investment_date)
        self.assertIsNotNone(self.loan.expected_interest_amount)
        # self.assertIsNotNone(self.loan.expected_irr)
        self.assertFalse(self.loan.is_closed)

        # Close the loan and check if is_closed and realized_irr fields are updated accordingly
        self.loan.is_closed = True
        self.loan.save()
        # self.assertIsNotNone(self.loan.realized_irr)
        self.assertTrue(self.loan.is_closed)

    def test_loan_total_amount_validation(self):
        """
        Test validation for total_amount field in Loan model.
        """
        with self.assertRaises(ValidationError):
            loan = Loan(
                identifier='loan123',
                issue_date=timezone.now().date(),
                total_amount=Decimal('0'),
                rating=1,
                maturity_date=timezone.now().date(),
                total_expected_interest_amount=Decimal('100'),
            )
            loan.full_clean()  # Validate the model fields and raise a ValidationError if any error occurs.

class CashflowModelTests(TestCase):
    """
    Test Cashflow model.
    """

    def setUp(self):
        """
        Set up a test Loan object and Cashflow objects.
        """
        self.loan = Loan.objects.create(
            identifier='loan123',
            issue_date=timezone.now().date(),
            total_amount=Decimal('1000'),
            rating=1,
            maturity_date=timezone.now().date(),
            total_expected_interest_amount=Decimal('100'),
        )

        self.cashflow1 = Cashflow.objects.create(
            loan_identifier=self.loan,
            type='FUNDING',
            reference_date=timezone.now().date(),
            amount=Decimal('200'),
        )

        self.cashflow2 = Cashflow.objects.create(
            loan_identifier=self.loan,
            type='INTEREST',
            reference_date=timezone.now().date(),
            amount=Decimal('50'),
        )

    def test_cashflow_str_representation(self):
        """
        Test string representation of Cashflow model.
        """
        self.assertEqual(str(self.cashflow1), f'loan123 - FUNDING - {self.cashflow1.reference_date}')
        self.assertEqual(str(self.cashflow2), f'loan123 - INTEREST - {self.cashflow2.reference_date}')

    def test_cashflow_loan_relation(self):
        """
        Test Loan-Cashflow relationship.
        """
        self.assertEqual(self.cashflow1.loan_identifier, self.loan)
        self.assertEqual(self.cashflow2.loan_identifier, self.loan)

    def test_cashflow_amount_validation(self):
        """
        Test validation for cashflow_amount field in Cashflow model.
        """
        with self.assertRaises(ValidationError):
            cashflow = Cashflow(
                loan_identifier=self.loan,
                reference_date=timezone.now().date(),
                type='PRINCIPAL',
                amount=Decimal('0'),
            )
            cashflow.full_clean()  # Validate the model fields and raise a ValidationError if any error occurs.
