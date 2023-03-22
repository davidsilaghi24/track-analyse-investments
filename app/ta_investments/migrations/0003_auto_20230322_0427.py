# Generated by Django 3.2.18 on 2023-03-22 04:27

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ta_investments', '0002_cashflow_loan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashflow',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='cashflow',
            name='loan_identifier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cashflows', to='ta_investments.loan', to_field='identifier'),
        ),
        migrations.AlterField(
            model_name='cashflow',
            name='type',
            field=models.CharField(choices=[('FUNDING', 'Funding'), ('REPAYMENT', 'Repayment')], max_length=20),
        ),
        migrations.AlterField(
            model_name='loan',
            name='expected_irr',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='identifier',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='rating',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]),
        ),
        migrations.AlterField(
            model_name='loan',
            name='realized_irr',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='loan',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='loan',
            name='total_expected_interest_amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]