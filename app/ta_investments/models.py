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

    def save(self, *args, **kwargs):
        if self.invested_amount is not None and self.investment_date is None:
            self.investment_date = timezone.now().date()

        if self.invested_amount is not None and self.expected_interest_amount is None:
            # Calculate expected_interest_amount and expected_irr
            self.expected_interest_amount = self.total_expected_interest_amount * (self.invested_amount / self.total_amount)

        if self.is_closed and self.realized_irr is None:
            # Calculate realized_irr
            pass

        super(Loan, self).save(*args, **kwargs)


class Cashflow(models.Model):
    loan_identifier = models.ForeignKey(Loan, on_delete=models.CASCADE)
    reference_date = models.DateField()
    type = models.CharField(max_length=20, choices=[("FUNDING", "Funding"), ("PRINCIPAL", "Principal Repayment"), ("INTEREST", "Interest Repayment")])
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.loan_identifier.identifier} - {self.type} - {self.reference_date}"
