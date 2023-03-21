"""
Database models
"""
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.core.validators import MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create, save and return a new user
        """
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_superuser(self, email, password):
        """
        Create and return a new superuser
        """
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Loan(models.Model):
    identifier = models.CharField(max_length=100, unique=True)
    issue_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(9)])
    maturity_date = models.DateField()
    total_expected_interest_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    invested_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    investment_date = models.DateField(null=True, blank=True)
    expected_interest_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    expected_irr = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    realized_irr = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.identifier

    def calculate_expected_irr(self):
        cashflows = [
            (self.investment_date, -self.invested_amount),
            (self.maturity_date, self.invested_amount + self.expected_interest_amount)
        ]
        return xirr(cashflows) * 100

    def calculate_realized_irr(self, cashflows):
        return xirr(cashflows) * 100

    def check_is_closed(self, cashflows):
        total_repayments = sum(amount for date, amount in cashflows if amount > 0)
        expected_amount = self.invested_amount + self.expected_interest_amount
        return total_repayments >= expected_amount

    def save(self, *args, **kwargs):
        if self.invested_amount is not None and self.investment_date is None:
            funding_cashflow = self.cashflow_set.filter(type="FUNDING").first()
            if funding_cashflow:
                self.investment_date = funding_cashflow.reference_date
                self.invested_amount = funding_cashflow.amount

        if self.invested_amount is not None and self.expected_interest_amount is None:
            self.expected_interest_amount = self.total_expected_interest_amount * (self.invested_amount / self.total_amount)

        if self.invested_amount is not None and self.expected_irr is None:
            self.expected_irr = self.calculate_expected_irr()

        if not self.is_closed:
            cashflows = [(cf.reference_date, cf.amount) for cf in self.cashflow_set.exclude(type="FUNDING")]
            if cashflows:
                self.is_closed = self.check_is_closed(cashflows)
                if self.is_closed:
                    self.realized_irr = self.calculate_realized_irr(cashflows)

        super(Loan, self).save(*args, **kwargs)


class Cashflow(models.Model):
    loan_identifier = models.ForeignKey(Loan, on_delete=models.CASCADE)
    reference_date = models.DateField()
    type = models.CharField(max_length=20, choices=[("FUNDING", "Funding"), ("PRINCIPAL", "Principal Repayment"), ("INTEREST", "Interest Repayment")])
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.loan_identifier.identifier} - {self.type} - {self.reference_date}"
