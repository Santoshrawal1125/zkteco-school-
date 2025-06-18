from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import (
    User, School, SchoolAdmin, Department,
    StudentClass, Staff, Student, Device, Attendance, Shift
)
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule
import json


# Custom user creation form
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')


# Custom user change form
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')


# Custom user admin
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ('username', 'email', 'role', 'is_staff', 'is_superuser')
    list_filter = ('role', 'is_staff', 'is_superuser')

    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {'fields': ('role',)}),
    )

    # ✅ FIX: remove usable_password from add_fieldsets
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )

    # Optional: Ensure password gets hashed if raw
    def save_model(self, request, obj, form, change):
        password = form.cleaned_data.get('password')
        if password and not password.startswith('pbkdf2_'):
            obj.set_password(password)
        super().save_model(request, obj, form, change)


# Register everything
admin.site.register(User, UserAdmin)
admin.site.register(School)
admin.site.register(SchoolAdmin)
admin.site.register(Department)
admin.site.register(StudentClass)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Device)
admin.site.register(Attendance)
admin.site.register(Shift)

# admin.py

from django.contrib import admin
from .models import Holiday


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('school', 'name', 'start_date', 'end_date')
    list_filter = ('school', 'start_date', 'end_date')
