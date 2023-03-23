"""
Database models
"""
import uuid
from django.forms import ValidationError
from pyxirr import xirr
from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.core.validators import MinValueValidator, MaxValueValidator

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    Group.objects.get_or_create(name='Investor')
    Group.objects.get_or_create(name='Analyst')

class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, user_type=None, **extra_fields):
        """
        Create, save and return a new user
        """
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), user_type=user_type, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)

        GROUP_MAPPING = {
        'Investor': 'Investor',
        'Analyst': 'Analyst',
        }

        group_name = GROUP_MAPPING.get(user_type)
        if group_name:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)

        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'Admin')  # Add this line to set a default user_type

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    USER_TYPES = (
        ('Investor', 'Investor'),
        ('Analyst', 'Analyst'),
        ('Admin', 'Admin')
    )

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=20, choices=USER_TYPES, default='Investor')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()
    USERNAME_FIELD = 'email'


class Loan(models.Model):
    identifier = models.CharField(max_length=100, unique=True, editable=False)
    issue_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 10)])
    maturity_date = models.DateField()
    total_expected_interest_amount = models.DecimalField(max_digits=10, decimal_places=2)

    investment_date = models.DateField(blank=True, null=True)
    invested_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expected_interest_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    expected_irr = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    realized_irr = models.DecimalField(max_digits=10, decimal_places=6, blank=True, null=True)
    is_closed = models.BooleanField(default=False)

    def calculate_fields(self):
        funding_cash_flow = self.cashflows.filter(type="FUNDING").first()
        if funding_cash_flow:
            self.investment_date = funding_cash_flow.reference_date
            self.invested_amount = funding_cash_flow.amount
            self.expected_interest_amount = Decimal(self.total_expected_interest_amount) * (Decimal(self.invested_amount) / Decimal(self.total_amount))

            dates = [self.investment_date, self.maturity_date]
            amounts = [-self.invested_amount, self.invested_amount + self.expected_interest_amount]
            self.expected_irr = xirr(dates, amounts)

            self.is_closed = self.check_is_closed()

            if self.is_closed:
                realized_cashflows = [(cf.reference_date, cf.amount) for cf in self.cashflows.all()]
                realized_dates = [cf[0] for cf in realized_cashflows]
                realized_amounts = [cf[1] for cf in realized_cashflows]
                self.realized_irr = xirr(realized_dates, realized_amounts)

    def check_is_closed(self):
        funding_cash_flow = self.cashflows.filter(type="Funding").first()
        if not funding_cash_flow:
            return False

        repayment_cash_flow = self.cashflows.filter(type="Repayment").first()
        if not repayment_cash_flow:
            return False

        total_repaid_amount = sum([cf.amount for cf in self.cashflows.filter(type="Repayment")])
        expected_amount = Decimal(funding_cash_flow.amount) * -1 + self.expected_interest_amount
        return total_repaid_amount >= expected_amount

    def save(self, *args, **kwargs):
        super(Loan, self).save(*args, **kwargs)

class Cashflow(models.Model):
    TYPES = (
        ("FUNDING", "Funding"),
        ("REPAYMENT", "Repayment"),
    )
    loan_identifier = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='cashflows', to_field='identifier')
    type = models.CharField(choices=TYPES, max_length=20)
    reference_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        super(Cashflow, self).save(*args, **kwargs)
        loan = self.loan_identifier
        loan.calculate_fields()
        loan.save()

    # stuff I don't have time to immplement: empty the Loan calculated fields
    # if Cashflow object is deleted.