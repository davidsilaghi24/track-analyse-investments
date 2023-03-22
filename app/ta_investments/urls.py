from django.urls import path, re_path
from .views import (
    LoanListCreateView,
    LoanDetailView,
    CashflowListCreateView,
    CashflowDetailView,
    LoansCSVUploadView,
    CashflowCSVUploadView
)

urlpatterns = [
    path('loans/', LoanListCreateView.as_view(), name='loan-list-create'),
    path('loans/<int:pk>/', LoanDetailView.as_view(), name='loan-detail'),
    path('cashflows/', CashflowListCreateView.as_view(), name='cashflow-list-create'),
    path('cashflows/<int:pk>/', CashflowDetailView.as_view(), name='cashflow-detail'),
    path('upload/loan-csv/', LoansCSVUploadView.as_view(), name='loan_csv_upload'),
    path('upload/cashflow-csv/', CashflowCSVUploadView.as_view(), name='cashflow_csv_upload'),
]
