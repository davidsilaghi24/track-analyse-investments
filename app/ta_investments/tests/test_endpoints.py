import uuid
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Loan, Cashflow, User


class LoanAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(email='testuser@example.com', password='testpassword', user_type='Investor')
        self.client.force_authenticate(user=self.test_user)
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

    def test_list_loans(self):
        response = self.client.get(reverse('loan-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_loan(self):
        loan = Loan.objects.create(**self.loan_data)
        response = self.client.get(reverse('loan-detail', kwargs={'pk': loan.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['identifier'], loan.identifier)

    def test_update_loan(self):
        loan = Loan.objects.create(**self.loan_data)
        updated_data = self.loan_data.copy()
        updated_data['rating'] = 5
        response = self.client.put(reverse('loan-detail', kwargs={'pk': loan.pk}), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan.refresh_from_db()
        self.assertEqual(loan.rating, 5)

    def test_delete_loan(self):
        loan = Loan.objects.create(**self.loan_data)
        response = self.client.delete(reverse('loan-detail', kwargs={'pk': loan.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Loan.objects.count(), 0)

class CashflowAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(email='testuser@example.com', password='testpassword', user_type='Investor')
        self.client.force_authenticate(user=self.test_user)
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

    def test_list_cashflows(self):
        Cashflow.objects.create(loan_identifier=self.loan, reference_date=self.cashflow_data['reference_date'], type=self.cashflow_data['type'], amount=self.cashflow_data['amount'])
        response = self.client.get(reverse('cashflow-list-create'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_cashflow(self):
        cashflow = Cashflow.objects.create(loan_identifier=self.loan, reference_date=self.cashflow_data['reference_date'], type=self.cashflow_data['type'], amount=self.cashflow_data['amount'])
        response = self.client.get(reverse('cashflow-detail', kwargs={'pk': cashflow.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['loan_identifier']), cashflow.loan_identifier.identifier)

    def test_update_cashflow(self):
        cashflow = Cashflow.objects.create(loan_identifier=self.loan, reference_date=self.cashflow_data['reference_date'], type=self.cashflow_data['type'], amount=self.cashflow_data['amount'])
        updated_data = self.cashflow_data.copy()
        updated_data['amount'] = 90000.00
        response = self.client.put(reverse('cashflow-detail', kwargs={'pk': cashflow.pk}), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cashflow.refresh_from_db()
        self.assertEqual(cashflow.amount, 90000.00)

    def test_delete_cashflow(self):
        cashflow = Cashflow.objects.create(loan_identifier=self.loan, reference_date=self.cashflow_data['reference_date'], type=self.cashflow_data['type'], amount=self.cashflow_data['amount'])
        response = self.client.delete(reverse('cashflow-detail', kwargs={'pk': cashflow.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cashflow.objects.count(), 0)


class AnalystCannotCreateLoanTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.analyst_user = User.objects.create_user(email='analyst@example.com', password='testpassword', user_type='Analyst')
        self.client.force_authenticate(user=self.analyst_user)
        self.loan_data = {
            "identifier": "123e4567-e89b-12d3-a456-426614174000",
            "issue_date": "2023-01-01",
            "rating": 6,
            "maturity_date": "2023-12-31",
            "total_amount": 100000.00,
            "total_expected_interest_amount": 5000.00,
        }

    def test_analyst_cannot_create_loan(self):
        response = self.client.post(reverse('loan-list-create'), self.loan_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Loan.objects.count(), 0)


class TokenAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(email='testuser@example.com', password='testpassword', user_type='Investor')

    def test_obtain_token(self):
        response = self.client.post('/api/token/', {'email': 'testuser@example.com', 'password': 'testpassword'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)