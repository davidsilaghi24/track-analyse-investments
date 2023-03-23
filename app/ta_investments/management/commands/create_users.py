import os
import secrets
import string

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from ta_investments.models import User


def generate_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(characters) for _ in range(length))


class Command(BaseCommand):
    help = "Create standard Investor and Analyst users if they don't exist."

    def handle(self, *args, **options):
        readme_path = os.path.join(settings.BASE_DIR, "UserReadMe.md")

        if not User.objects.filter(email="investor@example.com").exists():
            password_length = secrets.choice(range(6, 11))
            investor_password = generate_password(password_length)

            investor = User.objects.create_user(
                email="investor@example.com",
                password=investor_password,
                user_type="Investor",
            )
            investor_group = Group.objects.get(name="Investor")
            investor.groups.add(investor_group)
            investor.save()
            self.stdout.write(self.style.SUCCESS("Investor user created."))

            # Save the investor credentials to UserReadMe.md
            with open(readme_path, "w") as f:
                f.write("Investor user credentials:\n")
                f.write(f"Email: investor@example.com\n")
                f.write(f"Password: {investor_password}\n")
                f.write("\n")

        if not User.objects.filter(email="analyst@example.com").exists():
            password_length = secrets.choice(range(6, 11))
            analyst_password = generate_password(password_length)

            analyst = User.objects.create_user(
                email="analyst@example.com",
                password=analyst_password,
                user_type="Analyst",
            )
            analyst_group = Group.objects.get(name="Analyst")
            analyst.groups.add(analyst_group)
            analyst.save()
            self.stdout.write(self.style.SUCCESS("Analyst user created."))

            # Save the analyst credentials to UserReadMe.md
            with open(readme_path, "a") as f:
                f.write("Analyst user credentials:\n")
                f.write(f"Email: analyst@example.com\n")
                f.write(f"Password: {analyst_password}\n")
                f.write("\n")

            with open(readme_path, "a") as f:
                f.write(
                    "Please change your password after logging in for the first time.\n")
