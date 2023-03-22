from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Loan, Cashflow


class LoanAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.loan_data = {
            "identifier": "123e4567-e89b-12d3-a456-426614174000",
            "issue_date": "2023-01-01",
            "rating": 6,
            "maturity_date": "2023-12-31",
            "total_amount": 100000.00,
            "total_expected_interest_amount": 5000.00,
        }

    def test_create_loan(self):
        response = self.client.post(reverse('loan-list-create'), self.loan_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)

    # Additional tests for other operations like list, retrieve, update and delete

class CashflowAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.loan = Loan.objects.create(**{
            "identifier": "123e4567-e89b-12d3-a456-426614174000",
            "issue_date": "2023-01-01",
            "rating": 6,
            "maturity_date": "2023-12-31",
            "total_amount": 100000.00,
            "total_expected_interest_amount": 5000.00,
        })

        self.cashflow_data = {
            "loan_identifier": self.loan.identifier,
            "reference_date": "2023-01-01",
            "type": "FUNDING",
            "amount": 100000.00,
        }

    def test_create_cashflow(self):
        response = self.client.post(reverse('cashflow-list-create'), self.cashflow_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cashflow.objects.count(), 1)

        # Now that we've created a cash flow, the Loan object should have calculated fields populated.
        self.loan.refresh_from_db()
        self.assertIsNotNone(self.loan.investment_date)
        self.assertIsNotNone(self.loan.invested_amount)
        self.assertIsNotNone(self.loan.expected_interest_amount)
        self.assertIsNotNone(self.loan.expected_irr)

    # Additional tests for other operations like list, retrieve, update and delete
