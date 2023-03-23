# track-analyse-investments

This is a simple backend-only application that allows an investor to track and analyze their investments. The application is built using Django, Django REST framework, drf-spectacular, Celery, Redis, and docker-compose.

# Description

The application allows investors to invest their money in different financial instruments, with a focus on loans. Each loan has one single expected repayment, meaning that the investor lends money to a customer or business and then expects a repayment on the maturity date of that loan.

The main entities in the application are Loan and CashFlow. A Loan contains the information of a loan in which the investor has invested, while a CashFlow is an event in the lifecycle of the loan. The application considers two types of cash flows: funding and repayment.

# Entities Attributes

The following attributes are calculated for the Loan entity:

investment_date: calculated only when the loan is created and equal to the reference date of the funding cash flow of the loan.
invested_amount: calculated only when the loan is created and equal to the amount of the funding cash flow of the loan.
expected_interest_amount: calculated only when the loan is created and equal to total_expected_interest_amount \* (invested_amount / total_amount).
is_closed: calculated whenever a new cash flow for the loan is received. If the loan has received a total repaid amount equal to the expected amount (invested_amount + expected_interest_amount) or higher, it is considered closed. Otherwise, it is still open.
expected_irr: calculated only when the loan is created and uses the XIRR function. For the expected IRR, the cash flows that should be used are:
The funding
Date: reference_date
Amount: funding amount (negative)
The expected repayment:
Date: maturity_date
Amount: invested_amount + expected_interest_amount (positive)
realized_irr: similar to the expected_irr, calculated only when the loan is closed. The cash flows that should be used are:
The funding
Date: reference_date
Amount: funding amount (negative)
The repayment
Date: reference_date
Amount: repayment amount (positive)

# Functional Requirements

The following functionalities are available in the application:

Allow the user to upload the data of their investments in the application.
The user will provide 2 CSV files: one containing the loans and one containing the cash flows of the loans.
The loan fields will be calculated as necessary.
Allow the user to create a repayment for a loan, not through the CSV file.
The necessary loan calculations will take place in this case as well.
Allow the user to view their loans and filter them by any attribute.
Allow the user to view the cash flows and filter them by any attribute.
Allow the user to view statistics on their investments, including:
Number of loans
Total invested amount (all loans)
Current invested amount (only open loans)
Total repaid amount (all loans)
Average realized IRR (weighted average of realized IRR, using the loan invested amount as weight)
Consider only closed loans.

# Non-functional Requirements

The following non-functional requirements apply to the application:

The application should expose a REST API for the required functionalities.
The application should support authentication and authorization.
There are 2 types of users: Investor (can do anything on the application) and Analyst (read-only permissions).
The processing of the CSV files should happen asynchronously using Celery.
The statistics should be stored in a cache
