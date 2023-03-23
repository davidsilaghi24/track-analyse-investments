import csv
import io

from rest_framework import views, response, status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework import generics, permissions, status
import csv
import io

from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Loan, Cashflow
from .permissions import IsInvestor, IsAnalyst
from .serializers import LoanSerializer, CashflowSerializer
from django.core.exceptions import ValidationError
from rest_framework import permissions
from rest_framework.parsers import MultiPartParser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes


class LoanListCreateView(generics.ListCreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['identifier', 'issue_date', 'rating', 'maturity_date']
    ordering_fields = '__all__'
    permission_classes = [permissions.IsAuthenticated, IsInvestor, IsAnalyst]

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
    permission_classes = [permissions.IsAuthenticated, IsInvestor, IsAnalyst]

    @extend_schema(summary='Retrieve, update, or delete a loan')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CashflowListCreateView(generics.ListCreateAPIView):
    queryset = Cashflow.objects.all()
    serializer_class = CashflowSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['loan_identifier__identifier', 'reference_date', 'type']
    ordering_fields = '__all__'
    permission_classes = [permissions.IsAuthenticated, IsInvestor, IsAnalyst]

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
    permission_classes = [permissions.IsAuthenticated, IsInvestor, IsAnalyst]

    @extend_schema(summary='Retrieve, update, or delete a cash flow')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class LoansCSVUploadView(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary='Upload Loans CSV file',
        operation_id='upload_loans_csv',
        request=OpenApiTypes.BINARY,
        responses={201: 'Loans CSV file uploaded successfully'}
    )
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')

        # check if file was uploaded
        if not csv_file:
            return Response({'error': 'CSV file is required'}, status=status.HTTP_400_BAD_REQUEST)

        # check if file extension is valid
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'Invalid file format. Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        # process the CSV file
        csv_content = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(csv_content))

        for row in csv_data:
            if list(row.keys()) == ['identifier', 'issue_date', 'total_amount', 'rating', 'maturity_date', 'total_expected_interest_amount']:
                loan = Loan.objects.create(
                    identifier=row['identifier'],
                    issue_date=row['issue_date'],
                    total_amount=row['total_amount'],
                    rating=row['rating'],
                    maturity_date=row['maturity_date'],
                    total_expected_interest_amount=row['total_expected_interest_amount']
                )
            else:
                return Response({'error': str('Wrong fields loans.csv file')}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Loans CSV file uploaded successfully'}, status=status.HTTP_201_CREATED)


class CashflowCSVUploadView(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary='Upload Cashflow CSV file',
        operation_id='upload_cashflow_csv',
        request=OpenApiTypes.BINARY,
        responses={201: 'Cashflow CSV file uploaded successfully'}
    )
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get('file')

        # check if file was uploaded
        if not csv_file:
            return Response({'error': 'CSV file is required'}, status=status.HTTP_400_BAD_REQUEST)

        # check if file extension is valid
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'Invalid file format. Please upload a CSV file.'}, status=status.HTTP_400_BAD_REQUEST)

        # process the CSV file
        csv_content = csv_file.read().decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(csv_content))

        for row in csv_data:
            if list(row.keys()) == ['loan_identifier' ,'reference_date', 'type', 'amount']:
                loan = Loan.objects.filter(identifier=row['loan_identifier']).first()
                if loan:
                    cashflow = Cashflow.objects.create(
                        loan_identifier=loan,
                        reference_date=row['reference_date'],
                        type=row['type'].upper(),
                        amount=row['amount']
                    )
                else:
                    return Response({'error': 'Loan with identifier {} not found'.format(row['loan_identifier'])}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': str('Wrong fields loans.csv file')}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Cashflow CSV file uploaded successfully'}, status=status.HTTP_201_CREATED)


class CreateRepaymentView(generics.CreateAPIView):
    queryset = Cashflow.objects.all()
    serializer_class = CashflowSerializer
    permission_classes = [permissions.IsAuthenticated, IsInvestor, IsAnalyst]

    def post(self, request, *args, **kwargs):
        loan_identifier = request.data.get('loan_identifier')
        loan = Loan.objects.filter(identifier=loan_identifier).first()

        if not loan:
            return Response({'error': 'Loan with identifier {} not found'.format(loan_identifier)}, status=status.HTTP_400_BAD_REQUEST)

        repayment_amount = request.data.get('amount')
        repayment_date = request.data.get('reference_date')

        cashflow = Cashflow.objects.create(
            loan_identifier=loan,
            reference_date=repayment_date,
            type='REPAYMENT',
            amount=repayment_amount
        )

        serializer = self.get_serializer(cashflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
