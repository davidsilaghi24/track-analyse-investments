from django.urls import path

from .views import (CashflowCSVUploadView, CashflowDetailView,
                    CashflowListCreateView, CreateRepaymentView,
                    LoanDetailView, LoanListCreateView, LoansCSVUploadView,
                    InvestmentStatisticsView)

urlpatterns = [
    path(
        "loans/",
        LoanListCreateView.as_view(),
        name="loan-list-create"),
    path(
        "loans/<int:pk>/",
        LoanDetailView.as_view(),
        name="loan-detail"),
    path(
        "cashflows/",
        CashflowListCreateView.as_view(),
        name="cashflow-list-create"),
    path(
        "cashflows/<int:pk>/",
        CashflowDetailView.as_view(),
        name="cashflow-detail"),
    path(
        "upload/loan-csv/",
        LoansCSVUploadView.as_view(),
        name="loan_csv_upload"),
    path(
        "upload/cashflow-csv/",
        CashflowCSVUploadView.as_view(),
        name="cashflow_csv_upload",
    ),
    path(
        "repayments/",
        CreateRepaymentView.as_view(),
        name="create_repayment"),
    path("investment-statistics/",
         InvestmentStatisticsView.as_view(),
         name="investment_statistics"),
]
