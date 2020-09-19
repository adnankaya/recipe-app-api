from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _
# internal
from core import models


class UserAdmin(BaseUserAdmin):

    list_display = ('username', 'last_login', 'email',
                    'is_admin', 'role',)
    ordering = ("username",)
    search_fields = ('username', 'email')

    filter_horizontal = ()

    fieldsets = (
        (None, {"fields": ('username', 'password')}),
        (_("Personal Info"), {"fields": ("email", "first_name", 'last_name',
                                         "role", "job_title"
                                         )}),
        (_("Permissions"),
         {"fields": ("is_active", "is_staff", "is_admin", "is_superuser",)}
         ),

        (_("Important Dates"), {"fields": ("last_login",)}),
    )

    add_fields = (
        (None, {
            'classes': {'wide', },
            'fields': ('email', 'password1', 'password2')
        })
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
