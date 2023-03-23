import csv
import io
import logging

from celery import shared_task
from ta_investments.models import Cashflow, Loan

logger = logging.getLogger(__name__)


@shared_task
def process_loans_csv(csv_content):
    csv_data = csv.DictReader(io.StringIO(csv_content))

    for row in csv_data:
        if list(row.keys()) == [
            "identifier",
            "issue_date",
            "total_amount",
            "rating",
            "maturity_date",
            "total_expected_interest_amount",
        ]:
            Loan.objects.create(
                identifier=row["identifier"],
                issue_date=row["issue_date"],
                total_amount=row["total_amount"],
                rating=row["rating"],
                maturity_date=row["maturity_date"],
                total_expected_interest_amount=row["total_expected_interest_amount"],
            )


@shared_task
def process_cashflow_csv(csv_content):
    csv_data = csv.DictReader(io.StringIO(csv_content))

    for row in csv_data:
        if list(row.keys()) == [
            "loan_identifier",
            "reference_date",
            "type",
            "amount",
        ]:
            loan = Loan.objects.filter(
                identifier=row["loan_identifier"]).first()
            if loan:
                Cashflow.objects.create(
                    loan_identifier=loan,
                    reference_date=row["reference_date"],
                    type=row["type"].upper(),
                    amount=row["amount"],
                )
            else:
                logger.warning(
                    f"Loan with identifier {row['loan_identifier']} not found")
        else:
            logger.warning("Wrong fields loans.csv file")
