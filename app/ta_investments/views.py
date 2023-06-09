from django.conf import settings
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import CashFlowFilter, LoanFilter
from .models import Cashflow, Loan
from .permissions import IsAnalyst, IsInvestor
from .serializers import (CashflowSerializer, InvestmentStatisticsSerializer,
                          LoanSerializer)
from .tasks import process_cashflow_csv, process_loans_csv
from .utils import calculate_investment_statistics


class LoanListCreateView(generics.ListCreateAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["identifier", "issue_date", "rating", "maturity_date"]
    ordering_fields = "__all__"
    permission_classes = [IsInvestor, IsAnalyst]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LoanFilter

    @extend_schema(
        summary="List and create loans",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search loans by identifier, issue_date, \
                    rating, or maturity_date",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description="Order loans by any attribute",
                required=False,
                type=str,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LoanDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [IsInvestor, IsAnalyst]

    @extend_schema(summary="Retrieve, update, or delete a loan")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CashflowListCreateView(generics.ListCreateAPIView):
    queryset = Cashflow.objects.all()
    serializer_class = CashflowSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["loan_identifier__identifier", "reference_date", "type"]
    ordering_fields = "__all__"
    permission_classes = [IsInvestor, IsAnalyst]
    filter_backends = [DjangoFilterBackend]
    filterset_class = CashFlowFilter

    @extend_schema(
        summary="List and create cash flows",
        parameters=[
            OpenApiParameter(
                name="search",
                description="Search cash flows by loan_identifier, \
                    reference_date, or type",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="ordering",
                description="Order cash flows by any attribute",
                required=False,
                type=str,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CashflowDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Cashflow.objects.all()
    serializer_class = CashflowSerializer
    permission_classes = [IsInvestor, IsAnalyst]

    @extend_schema(summary="Retrieve, update, or delete a cash flow")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class LoansCSVUploadView(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary="Upload Loans CSV file",
        operation_id="upload_loans_csv",
        request=OpenApiTypes.BINARY,
        responses={201: "Loans CSV file uploaded successfully"},
    )
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file")

        # check if file was uploaded
        if not csv_file:
            return Response(
                {"error": "CSV file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if file extension is valid
        if not csv_file.name.endswith(".csv"):
            return Response(
                {"error": "Invalid file format. Please upload a CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # process the CSV file
        process_loans_csv.delay(csv_file.read().decode("utf-8"))

        return Response(
            {"message": "Loans CSV file is being processed"},
            status=status.HTTP_202_ACCEPTED,
        )


class CashflowCSVUploadView(APIView):
    parser_classes = [MultiPartParser]

    @extend_schema(
        summary="Upload Cashflow CSV file",
        operation_id="upload_cashflow_csv",
        request=OpenApiTypes.BINARY,
        responses={201: "Cashflow CSV file uploaded successfully"},
    )
    def post(self, request, *args, **kwargs):
        csv_file = request.FILES.get("file")

        # check if file was uploaded
        if not csv_file:
            return Response(
                {"error": "CSV file is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # check if file extension is valid
        if not csv_file.name.endswith(".csv"):
            return Response(
                {"error": "Invalid file format. Please upload a CSV file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # read the CSV file
        csv_content = csv_file.read().decode("utf-8")

        # process the CSV file asynchronously using Celery
        process_cashflow_csv.delay(csv_content)

        return Response(
            {"message": "Cashflow CSV file uploaded successfully"},
            status=status.HTTP_201_CREATED,
        )


class CreateRepaymentView(generics.CreateAPIView):
    queryset = Cashflow.objects.all()
    serializer_class = CashflowSerializer
    permission_classes = [IsInvestor, IsAnalyst]

    def post(self, request, *args, **kwargs):
        loan_identifier = request.data.get("loan_identifier")
        loan = Loan.objects.filter(identifier=loan_identifier).first()

        if not loan:
            return Response({"error": "Loan with identifier {} not found".format(
                loan_identifier)}, status=status.HTTP_400_BAD_REQUEST, )

        repayment_amount = request.data.get("amount")
        repayment_date = request.data.get("reference_date")

        cashflow = Cashflow.objects.create(
            loan_identifier=loan,
            reference_date=repayment_date,
            type="REPAYMENT",
            amount=repayment_amount,
        )

        serializer = self.get_serializer(cashflow)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InvestmentStatisticsView(generics.ListAPIView):
    serializer_class = InvestmentStatisticsSerializer
    permission_classes = [IsInvestor, IsAnalyst]

    @extend_schema(
        description="Returns investment statistics for all loans and cashflows",
        responses={
            200: InvestmentStatisticsSerializer},
    )
    def get(self, request, *args, **kwargs):
        # Try to get investment statistics from cache
        investment_statistics = cache.get(
            settings.INVESTMENT_STATISTICS_CACHE_KEY)

        if investment_statistics is not None:
            return Response(investment_statistics, status=status.HTTP_200_OK)

        # If the cache is empty, calculate investment statistics
        loans = Loan.objects.all()
        cashflows = Cashflow.objects.all()
        investment_statistics = calculate_investment_statistics(
            loans, cashflows)

        # Store the statistics in the cache for 5 minutes
        cache.set(
            settings.INVESTMENT_STATISTICS_CACHE_KEY,
            investment_statistics,
            300,
        )

        return Response(investment_statistics, status=status.HTTP_200_OK)
