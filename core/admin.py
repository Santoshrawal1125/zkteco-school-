from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import admin
from .models import (
    User, School, SchoolAdmin, Department,
    StudentClass, Staff, Student, Device, Attendance
)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')


class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    # This ensures password gets hashed on creation AND update
    def save_model(self, request, obj, form, change):
        password = form.cleaned_data.get('password')
        if password and not password.startswith('pbkdf2_'):
            obj.set_password(password)
        super().save_model(request, obj, form, change)


admin.site.register(User, UserAdmin)
admin.site.register(School)
admin.site.register(SchoolAdmin)
admin.site.register(Department)
admin.site.register(StudentClass)
admin.site.register(Staff)
admin.site.register(Student)
admin.site.register(Device)
admin.site.register(Attendance)
