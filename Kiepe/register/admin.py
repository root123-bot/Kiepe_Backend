from django.contrib import admin
from .models import *

# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'joined', 'email', 'is_superuser')
    date_hierarchy = 'joined'
    list_filter = ('joined',    )
    search_fields = ('email', 'phone_number')

    fieldsets = (
        (None, {
            'fields': (
                'email', 'password'
            ),
        }),
        ('User status', {
            'fields': (
                'is_staff', 'is_superuser', 'is_active'
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserOTP)