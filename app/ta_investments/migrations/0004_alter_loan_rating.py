# Generated by Django 3.2.18 on 2023-03-22 04:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ta_investments", "0003_auto_20230322_0427"),
    ]

    operations = [
        migrations.AlterField(
            model_name="loan",
            name="rating",
            field=models.IntegerField(
                choices=[
                    (1, 1),
                    (2, 2),
                    (3, 3),
                    (4, 4),
                    (5, 5),
                    (6, 6),
                    (7, 7),
                    (8, 8),
                    (9, 9),
                ]
            ),
        ),
    ]
