from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .models import Loan, Cashflow
from .serializers import LoanSerializer, CashflowSerializer

class LoanListCreateView(generics.ListCreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['identifier', 'issue_date', 'rating', 'maturity_date']
    ordering_fields = '__all__'

    @extend_schema(
        summary='List and create loans',
        parameters=[
            OpenApiParameter(name='search', description='Search loans by identifier, issue_date, rating, or maturity_date', required=False, type=str),
            OpenApiParameter(name='ordering', description='Order loans by any attribute', required=False, type=str),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class LoanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer

    @extend_schema(summary='Retrieve, update, or delete a loan')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CashflowListCreateView(generics.ListCreateAPIView):
    queryset = Cashflow.objects.all()
    serializer_class = CashflowSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['loan_identifier__identifier', 'reference_date', 'type']
    ordering_fields = '__all__'

    @extend_schema(
        summary='List and create cash flows',
        parameters=[
            OpenApiParameter(name='search', description='Search cash flows by loan_identifier, reference_date, or type', required=False, type=str),
            OpenApiParameter(name='ordering', description='Order cash flows by any attribute', required=False, type=str),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CashflowDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cashflow.objects.all()
    serializer_class = CashflowSerializer

    @extend_schema(summary='Retrieve, update, or delete a cash flow')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
