from django.urls import path
from . import views

urlpatterns = [
    path('loans/', views.LoanListCreateView.as_view(), name='loan-list-create'),
    path('loans/<int:pk>/', views.LoanDetailView.as_view(), name='loan-detail'),
    path('cashflows/', views.CashflowListCreateView.as_view(), name='cashflow-list-create'),
    path('cashflows/<int:pk>/', views.CashflowDetailView.as_view(), name='cashflow-detail'),
]
