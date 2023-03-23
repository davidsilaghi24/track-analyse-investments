import tempfile

from datetime import date
from decimal import Decimal
from pathlib import Path

from django.urls import reverse
from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Cashflow, Loan, User


class LoanAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            user_type="Investor")
        self.client.force_authenticate(user=self.test_user)
        self.loan_data = {
            "identifier": "L103",
            "issue_date": "2023-01-01",
            "rating": 6,
            "maturity_date": "2023-12-31",
            "total_amount": 100000.00,
            "total_expected_interest_amount": 5000.00,
        }

    def test_create_loan(self):
        response = self.client.post(
            reverse("loan-list-create"),
            self.loan_data,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Loan.objects.count(), 1)

    def test_list_loans(self):
        response = self.client.get(reverse("loan-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_loan(self):
        loan = Loan.objects.create(**self.loan_data)
        response = self.client.get(
            reverse(
                "loan-detail",
                kwargs={
                    "pk": loan.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["identifier"], loan.identifier)

    def test_update_loan(self):
        loan = Loan.objects.create(**self.loan_data)
        updated_data = self.loan_data.copy()
        updated_data["rating"] = 5
        response = self.client.put(
            reverse(
                "loan-detail",
                kwargs={
                    "pk": loan.pk}),
            updated_data,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        loan.refresh_from_db()
        self.assertEqual(loan.rating, 5)

    def test_delete_loan(self):
        loan = Loan.objects.create(**self.loan_data)
        response = self.client.delete(
            reverse("loan-detail", kwargs={"pk": loan.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Loan.objects.count(), 0)


class CashflowAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            user_type="Investor")
        self.client.force_authenticate(user=self.test_user)
        self.loan = Loan.objects.create(
            **{
                "identifier": "L101",
                "issue_date": "2023-01-01",
                "rating": 6,
                "maturity_date": "2023-12-31",
                "total_amount": 100000.00,
                "total_expected_interest_amount": 5000.00,
            }
        )

        self.cashflow_data = {
            "loan_identifier": self.loan.identifier,
            "reference_date": "2023-01-01",
            "type": "FUNDING",
            "amount": 100000.00,
        }

    def test_create_cashflow(self):
        response = self.client.post(
            reverse("cashflow-list-create"),
            self.cashflow_data,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cashflow.objects.count(), 1)

        # Now that we've created a cash flow, the Loan object should have
        # calculated fields populated.
        self.loan.refresh_from_db()
        self.assertIsNotNone(self.loan.investment_date)
        self.assertIsNotNone(self.loan.invested_amount)
        self.assertIsNotNone(self.loan.expected_interest_amount)
        self.assertIsNotNone(self.loan.expected_irr)

    def test_list_cashflows(self):
        Cashflow.objects.create(
            loan_identifier=self.loan,
            reference_date=self.cashflow_data["reference_date"],
            type=self.cashflow_data["type"],
            amount=self.cashflow_data["amount"],
        )
        response = self.client.get(reverse("cashflow-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_cashflow(self):
        cashflow = Cashflow.objects.create(
            loan_identifier=self.loan,
            reference_date=self.cashflow_data["reference_date"],
            type=self.cashflow_data["type"],
            amount=self.cashflow_data["amount"],
        )
        response = self.client.get(
            reverse(
                "cashflow-detail",
                kwargs={
                    "pk": cashflow.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            str(response.data["loan_identifier"]), cashflow.loan_identifier.identifier)

    def test_update_cashflow(self):
        cashflow = Cashflow.objects.create(
            loan_identifier=self.loan,
            reference_date=self.cashflow_data["reference_date"],
            type=self.cashflow_data["type"],
            amount=self.cashflow_data["amount"],
        )
        updated_data = self.cashflow_data.copy()
        updated_data["amount"] = 90000.00
        response = self.client.put(
            reverse("cashflow-detail", kwargs={"pk": cashflow.pk}),
            updated_data,
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cashflow.refresh_from_db()
        self.assertEqual(cashflow.amount, 90000.00)

    def test_delete_cashflow(self):
        cashflow = Cashflow.objects.create(
            loan_identifier=self.loan,
            reference_date=self.cashflow_data["reference_date"],
            type=self.cashflow_data["type"],
            amount=self.cashflow_data["amount"],
        )
        response = self.client.delete(
            reverse(
                "cashflow-detail",
                kwargs={
                    "pk": cashflow.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Cashflow.objects.count(), 0)


class AnalystCannotCreateLoanTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.analyst_user = User.objects.create_user(
            email="analyst@example.com",
            password="testpassword",
            user_type="Analyst")
        self.client.force_authenticate(user=self.analyst_user)
        self.loan_data = {
            "identifier": "L104",
            "issue_date": "2023-01-01",
            "rating": 6,
            "maturity_date": "2023-12-31",
            "total_amount": 100000.00,
            "total_expected_interest_amount": 5000.00,
        }

    def test_analyst_cannot_create_loan(self):
        response = self.client.post(
            reverse("loan-list-create"),
            self.loan_data,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Loan.objects.count(), 0)


class TokenAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            user_type="Investor")

    def test_obtain_token(self):
        response = self.client.post(
            "/api/token/", {"email": "testuser@example.com", "password": "testpassword"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)


class CsvUploadViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.resource_path = Path(__file__).parent / "resources"
        self.loan_csv = self.resource_path / "loans.csv"
        self.cashflow_csv = self.resource_path / "cash_flows.csv"
        self.test_user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            user_type="Investor")
        self.client.force_authenticate(user=self.test_user)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_upload_csv_files(self):
        with open(self.loan_csv, "rb") as f:
            response = self.client.post(
                "/api/ta_investments/upload/loan-csv/", {"file": f}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # assert that a loan object was created with the expected values
        loan = Loan.objects.first()
        self.assertEqual(loan.identifier, "L101")
        self.assertEqual(loan.issue_date, date(2021, 5, 1))
        self.assertEqual(loan.total_amount, Decimal("200000"))
        self.assertEqual(loan.rating, 1)
        self.assertEqual(loan.maturity_date, date(2021, 8, 1))
        self.assertEqual(loan.total_expected_interest_amount, Decimal("80"))

        with open(self.cashflow_csv, "rb") as f:
            response = self.client.post(
                "/api/ta_investments/upload/cashflow-csv/",
                {"file": f},
                format="multipart",
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # assert that a cashflow object was created with the expected values
        cashflow = Cashflow.objects.first()
        self.assertEqual(cashflow.loan_identifier.identifier, "L101")
        self.assertEqual(cashflow.reference_date, date(2021, 5, 1))
        self.assertEqual(cashflow.type, "FUNDING")
        self.assertEqual(cashflow.amount, Decimal("-100000.00"))

        # assert that the loan object has the expected calculated fields
        # populated
        loan.refresh_from_db()
        self.assertIsNotNone(loan.investment_date)
        self.assertIsNotNone(loan.invested_amount)
        self.assertIsNotNone(loan.expected_interest_amount)
        self.assertIsNotNone(loan.expected_irr)


class RepaymentAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            user_type="Investor")
        self.client.force_authenticate(user=self.test_user)
        self.loan = Loan.objects.create(
            **{
                "identifier": "L102",
                "issue_date": "2021-01-01",
                "rating": 6,
                "maturity_date": "2022-12-31",
                "total_amount": 100000.00,
                "total_expected_interest_amount": 5000.00,
            }
        )

        # Manually set the values for testing
        self.loan.investment_date = date(2023, 1, 1)
        self.loan.invested_amount = 100000.00
        self.loan.expected_interest_amount = 5000.00
        self.loan.expected_irr = 0.05
        self.loan.save()

        self.repayment_data = {
            "loan_identifier": self.loan.identifier,
            "amount": 1000.00,
            "reference_date": "2023-01-31",
        }

    def test_create_repayment(self):
        # Store initial values
        initial_expected_irr = self.loan.expected_irr

        response = self.client.post(
            reverse("create_repayment"),
            self.repayment_data,
            format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cashflow.objects.count(), 1)
        self.assertEqual(Cashflow.objects.first().type, "REPAYMENT")

        # Refresh the loan object and check if the values have changed
        self.loan.refresh_from_db()
        self.assertNotEqual(self.loan.expected_irr, initial_expected_irr)


class InvestmentStatisticsViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.test_user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
            user_type="Investor")
        self.client.force_authenticate(user=self.test_user)

        # Create a new Loan instance
        self.loan_data = {
            "identifier": "L001",
            "issue_date": date(2022, 1, 1),
            "total_amount": Decimal("10000"),
            "rating": 5,
            "maturity_date": date(2023, 1, 1),
            "total_expected_interest_amount": Decimal("1000"),
        }
        self.loan = Loan.objects.create(**self.loan_data)

        # Create a Cashflow instance associated with the Loan
        self.cashflow_data = {
            "loan_identifier": self.loan,
            "type": "FUNDING",
            "reference_date": date(2022, 1, 1),
            "amount": Decimal("10000"),
        }
        self.cashflow = Cashflow.objects.create(**self.cashflow_data)

    def test_investment_statistics_view(self):
        # Ensure that the cache is empty
        self.assertIsNone(cache.get('investment_statistics'))

        url = reverse("investment_statistics")
        response = self.client.get(url)

        # Assert that the response is successful and the data is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure that the cache has been set
        cached_data = cache.get('investment_statistics')
        self.assertIsNotNone(cached_data)

        # Create a new Loan and Cashflow
        loan_data = {
            "identifier": "L002",
            "issue_date": date(2022, 1, 1),
            "total_amount": Decimal("10000"),
            "rating": 5,
            "maturity_date": date(2023, 1, 1),
            "total_expected_interest_amount": Decimal("1000"),
        }
        loan = Loan.objects.create(**loan_data)

        cashflow_data = {
            "loan_identifier": loan,
            "type": "FUNDING",
            "reference_date": date(2022, 1, 1),
            "amount": Decimal("10000"),
        }
        cashflow = Cashflow.objects.create(**cashflow_data)

        # Ensure that the cache has been invalidated
        self.assertIsNone(cache.get('investment_statistics'))
