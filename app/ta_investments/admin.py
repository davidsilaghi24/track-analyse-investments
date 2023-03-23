from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from ta_investments import models


class UserAdmin(BaseUserAdmin):
    """
    Define the admin pages for users.
    """

    ordering = ["id"]
    list_display = [
        "email",
        "name",
        "is_active",
        "is_staff",
        "is_superuser",
        "display_groups",
    ]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                )
            },
        ),
        (_("Relevant dates"), {"fields": ("last_login",)}),
    )
    readonly_fields = ["last_login"]
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "name",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                )
            },
        ),
    )

    # Define a custom method to display the groups as a comma-separated list
    def display_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])

    # Set a short description for the display_groups column
    display_groups.short_description = "Groups"


admin.site.register(models.User, UserAdmin)
