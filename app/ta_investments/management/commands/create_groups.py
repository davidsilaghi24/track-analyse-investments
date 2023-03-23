from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create Investor and Analyst groups if they don't exist."

    def handle(self, *args, **options):
        if not Group.objects.filter(name="Investor").exists():
            investor_group = Group.objects.create(name="Investor")
            investor_permissions = Permission.objects.all()
            investor_group.permissions.set(investor_permissions)
            investor_group.save()
            self.stdout.write(self.style.SUCCESS("Investor group created."))

        if not Group.objects.filter(name="Analyst").exists():
            analyst_group = Group.objects.create(name="Analyst")
            analyst_permissions = Permission.objects.filter(
                content_type__app_label="ta_investments", codename__startswith="view_")
            analyst_group.permissions.set(analyst_permissions)
            analyst_group.save()
            self.stdout.write(self.style.SUCCESS("Analyst group created."))
