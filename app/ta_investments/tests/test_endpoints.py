# from django.urls import reverse
# from django.test import TestCase
# from rest_framework.test import APIClient
# from rest_framework import status
# from ta_investments.models import Loan, Cashflow

# class LoanEndpointTests(TestCase):

#     def setUp(self):
#         self.client = APIClient()

#     def test_create_loan(self):
#         url = reverse('loans-list-create')
#         payload = {'identifier': 'Loan1'}
#         response = self.client.post(url, payload, format='json')

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Loan.objects.count(), 1)
#         self.assertEqual(Loan.objects.get().identifier, 'Loan1')


# class CashflowEndpointTests(TestCase):

#     def setUp(self):
#         self.client = APIClient()
#         self.loan = Loan.objects.create(identifier='Loan1')

#     def test_create_cashflow(self):
#         url = reverse('cashflows-list-create')
#         payload = {
#             'loan_identifier': self.loan.id,
#             'date': '2023-03-20',
#             'amount': 100.0,
#         }
#         response = self.client.post(url, payload, format='json')

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Cashflow.objects.count(), 1)
#         cashflow = Cashflow.objects.get()
#         self.assertEqual(cashflow.loan_identifier, self.loan)
#         self.assertEqual(str(cashflow.date), '2023-03-20')
#         self.assertEqual(cashflow.amount, 100.0)

#     def test_bulk_upload_cashflows(self):
#         url = reverse('cashflows-bulk-upload')
#         payload = {
#             'loan_identifier': self.loan.id,
#             'cashflows': [
#                 {'date': '2023-03-20', 'amount': 100.0},
#                 {'date': '2023-03-21', 'amount': 200.0},
#             ],
#         }
#         response = self.client.post(url, payload, format='json')

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Cashflow.objects.count(), 2)
