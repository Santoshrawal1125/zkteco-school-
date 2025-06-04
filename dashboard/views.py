from datetime import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth import logout, get_user_model
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest
from django.utils.dateparse import parse_date, parse_time
# Authentication views
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from core.models import (
    School, StudentClass, Department, Device, Shift,
    SchoolAdmin, Staff, Student, Attendance
)
import random
import string

User = get_user_model()


def get_user_school(user):
    if user.role == 'school_admin':
        try:
            return user.schooladmin.school
        except SchoolAdmin.DoesNotExist:
            return None
    return None


# Dashboard
def dashboard(request):
    context = {}

    # Only add `school` for school admins
    if request.user.is_authenticated and request.user.role == 'school_admin':
        school = get_user_school(request.user)
        if school:
            context['school'] = school
    return render(request, 'dashboard/dashboard.html')


# Attendance views
def attendance(request):
    return render(request, 'attendance/attendance.html')


def student_attendance(request):
    return render(request, 'attendance/student_attendance.html')


def staff_attendance(request):
    return render(request, 'attendance/staff_attendance.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib import messages
from core.models import School, Staff, Department, Shift, User


def add_staff(request, school_id):
    school = get_object_or_404(School, id=school_id)

    # Get department_id from GET request if available
    department_id = request.GET.get('department_id')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        position = request.POST.get('position')
        department_id = request.POST.get('department')  # override from POST
        shift_id = request.POST.get('shift')

        password = f"{username}@123"

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different username.")
            return redirect(request.path)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role='staff'
            )

            Staff.objects.create(
                user=user,
                school=school,
                position=position,
                department_id=department_id,
                shift_id=shift_id
            )

            messages.success(request, f"Staff added successfully. Default password: {password}")
            return redirect('school_staffs', school_id=school.id, department_id=department_id)

        except IntegrityError:
            messages.error(request, "An error occurred while adding the staff. Please try again.")
            return redirect(request.path)

    context = {
        'school': school,
        'school_id': school.id,
        'department_id': department_id,
        'departments': Department.objects.filter(school=school),
        'shifts': Shift.objects.filter(school=school),
    }
    return render(request, 'staff/add_staff.html', context)


# School views
def school(request):
    schools = School.objects.all()
    return render(request, 'school/school.html', {'schools': schools})


def add_school(request):
    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get('address')

        if name and address:
            School.objects.create(name=name, address=address)
            messages.success(request, "School added successfully!")
            return redirect('school')
        else:
            messages.error(request, "Both name and address are required.")

    return render(request, 'school/add_school.html')


def school_details(request, pk):
    school = get_object_or_404(School, pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')

        if name and address:
            school.name = name
            school.address = address
            school.save()
            messages.success(request, "School updated successfully.")
            return redirect('school')

    return render(request, 'school/school_details.html', {'school': school})


def school_delete(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == "POST":
        school.delete()
        messages.success(request, "School has been deleted successfully.")
        return redirect('school')
    return redirect('school_details', pk=pk)


def student_and_staff(request, school_id=None):
    user = request.user

    # Determine the correct school ID based on user role
    if user.role == 'school_admin':
        school_id = request.session.get('school_id')
        if not school_id:
            return HttpResponseBadRequest("No school assigned to your account.")

    elif user.role == 'admin':
        if not school_id:
            return HttpResponseBadRequest("Please provide a school to view.")

    else:
        # Print for debugging, you can remove this later
        print("User role:", user.role)
        return HttpResponseForbidden("Access denied.")

    # Fetch the school
    school = get_object_or_404(School, id=school_id)

    # Fetch students and staff of this school
    students = Student.objects.filter(school=school)
    staff = Staff.objects.filter(school=school)

    context = {
        'school': school,
        'students': students,
        'staff': staff,
    }

    return render(request, 'school/studentandstaff.html', context)


# Staff views by school
def school_staffs(request, school_id, department_id):
    school = get_object_or_404(School, id=school_id)
    department = get_object_or_404(Department, id=department_id)
    user_school = get_user_school(request.user)
    if request.user.role == 'school_admin' and school != user_school:
        return HttpResponseForbidden("You are not allowed to access this school's data.")

    staffs = Staff.objects.filter(school=school, department=department)

    return render(request, 'school/staff_acc_to_school.html',
                  {'school': school, department: 'department', 'staffs': staffs})


# Classes by school
def school_student_classes(request, school_id):
    school = get_object_or_404(School, id=school_id)
    student_classes = StudentClass.objects.filter(school=school)
    return render(request, 'school/school_classes.html', {'school': school, 'student_classes': student_classes})


# Students by classes

def school_class_student(request, school_id, student_class_id):
    school = get_object_or_404(School, id=school_id)
    student_class = get_object_or_404(StudentClass, id=student_class_id)
    students = Student.objects.filter(school=school, student_class=student_class)
    return render(request, 'school/studentbyclass.html', {
        'school': school,
        'student_class': student_class,
        'students': students
    })


# CRUD FOR CLASS

# Add a new class
def add_class(request, school_id):
    school = get_object_or_404(School, id=school_id)
    shifts = Shift.objects.filter(school=school)  # Get only shifts of this school

    if request.method == 'POST':
        name = request.POST.get('name')
        shift_id = request.POST.get('shift')

        if name:
            new_class = StudentClass(name=name, school=school)
            if shift_id:
                new_class.shift_id = shift_id
            new_class.save()
            return redirect('school_student_classes', school_id=school.id)
        else:
            error = "Class name is required."
            return render(request, 'school/add_class.html', {
                'school': school,
                'error': error,
                'name': name,
                'shift_id': shift_id,
                'shifts': shifts
            })

    return render(request, 'school/add_class.html', {'school': school, 'shifts': shifts})


# Edit an existing class
# ✅ Edit Class View
def edit_class(request, school_id, class_id):
    school = get_object_or_404(School, id=school_id)
    student_class = get_object_or_404(StudentClass, id=class_id, school=school)
    shifts = Shift.objects.filter(school=school)

    if request.method == 'POST':
        name = request.POST.get('name')
        shift_id = request.POST.get('shift')

        if name:
            student_class.name = name
            student_class.shift_id = shift_id if shift_id else None
            student_class.save()
            return redirect('school_student_classes', school_id=school.id)
        else:
            error = "Class name is required."
            return render(request, 'school/edit_class.html', {
                'school': school,
                'student_class': student_class,
                'error': error,
                'shifts': shifts
            })

    return render(request, 'school/edit_class.html', {
        'school': school,
        'student_class': student_class,
        'shifts': shifts
    })


# Delete a class
# ✅ Delete Class View
def delete_class(request, school_id, class_id):
    school = get_object_or_404(School, id=school_id)
    student_class = get_object_or_404(StudentClass, id=class_id, school=school)

    if request.method == 'POST':
        student_class.delete()
    return redirect('school_student_classes', school_id=school.id)


# Add a new department to a school
def add_department(request, school_id):
    school = get_object_or_404(School, id=school_id)

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Department.objects.create(name=name, school=school)
            return redirect('school_departments', school_id=school.id)

    return render(request, 'departments/add_department.html', {'school': school})


# Department views
def departments(request):
    departments = Department.objects.select_related('school').all()
    schools = School.objects.all()
    return render(request, 'departments/departments.html', {'departments': departments, 'schools': schools})


def school_departments(request, school_id):
    school = get_object_or_404(School, id=school_id)
    departments = Department.objects.filter(school=school)
    return render(request, 'departments/school_departments.html', {'school': school, 'departments': departments})


def edit_department(request, school_id, department_id):
    school = get_object_or_404(School, id=school_id)
    department = get_object_or_404(Department, id=department_id, school=school)

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            department.name = name
            department.save()
            return redirect('school_departments', school_id=school.id)
        else:
            error = "Name cannot be empty."
            return render(request, 'departments/edit_department.html', {
                'department': department,
                'school': school,
                'error': error
            })

    return render(request, 'departments/edit_department.html', {
        'department': department,
        'school': school
    })


def delete_department(request, school_id, department_id):
    school = get_object_or_404(School, id=school_id)
    department = get_object_or_404(Department, id=department_id, school=school)

    if request.method == 'POST':
        department.delete()
        return redirect('school_departments', school_id=school.id)

    return render(request, 'departments/confirm_delete_department.html', {'department': department, 'school': school})


# Device views
def school_list(request):
    schools = School.objects.all()
    return render(request, 'device/school_list.html', {'schools': schools})


def devices_by_school(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    devices = Device.objects.filter(school=school)
    return render(request, 'device/devices_by_school.html', {'school': school, 'devices': devices})


@login_required
def add_device(request, school_id):
    school = get_object_or_404(School, id=school_id)

    if request.method == 'POST':
        serial_number = request.POST.get('serial_number')
        location = request.POST.get('location')

        if not serial_number:
            return HttpResponseBadRequest("Serial number is required.")

        Device.objects.create(
            school=school,
            serial_number=serial_number,
            location=location
        )
        return redirect('devices_by_school', school_id=school.id)

    return render(request, 'device/add_device.html', {'school': school})


@login_required
def edit_device(request, device_id):
    device = get_object_or_404(Device, id=device_id)

    if request.method == 'POST':
        serial_number = request.POST.get('serial_number')
        location = request.POST.get('location')

        if not serial_number:
            return HttpResponseBadRequest("Serial number is required.")

        device.serial_number = serial_number
        device.location = location
        device.save()
        return redirect('devices_by_school', school_id=device.school.id)

    return render(request, 'device/edit_device.html', {
        'school': device.school,
        'device': device
    })


@login_required
def delete_device(request, device_id):
    device = get_object_or_404(Device, id=device_id)
    school_id = device.school.id
    device.delete()
    return redirect('devices_by_school', school_id=school_id)


# Shift views


def shift_list(request, school_id=None):
    user = request.user

    if user.role == 'school_admin':
        school_id = request.session.get('school_id')
        if not school_id:
            return HttpResponseBadRequest("No school assigned to your account.")

    elif user.role == 'admin':
        if not school_id:
            return HttpResponseBadRequest("Please provide a school to view.")
    else:
        return HttpResponseForbidden("Access Denied.")

    # Get the school object to validate school_id
    school = get_object_or_404(School, id=school_id)

    # Get all shifts for this school ordered by school name and start_time
    shifts = Shift.objects.filter(school=school).order_by('school__name', 'start_time')

    return render(request, 'shift/shift_list.html', {'shifts': shifts})


# User management views
def user_list(request):
    users = User.objects.all()
    return render(request, 'user/user_list.html', {'users': users})


def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        school_id = request.POST.get('school')
        school = School.objects.filter(id=school_id).first()

        password = f"{username}@123" if role == 'student' else request.POST.get('password')
        user = User.objects.create_user(username=username, email=email, password=password, role=role)

        if role == 'school_admin':
            SchoolAdmin.objects.create(user=user, school=school)
        elif role == 'staff':
            department_id = request.POST.get('department')
            position = request.POST.get('position')
            shift_id = request.POST.get('shift')
            Staff.objects.create(user=user, school=school, department_id=department_id, position=position,
                                 shift_id=shift_id)
        elif role == 'student':
            student_class_id = request.POST.get('student_class')
            Student.objects.create(user=user, school=school, student_class_id=student_class_id)

        msg = f"{role.capitalize()} user added successfully. Default password is: {password}" if role != 'school_admin' else "User added successfully."
        messages.success(request, msg)
        return redirect('user_list')

    context = {
        'schools': School.objects.all(),
        'departments': Department.objects.all(),
        'classes': StudentClass.objects.all(),
        'shifts': Shift.objects.all(),
    }
    return render(request, 'user/add_user.html', context)


def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.role = request.POST.get('role')
        user.save()
        messages.success(request, 'User updated successfully.')
        return redirect('user_list')

    context = {
        'user_obj': user,
        'schools': School.objects.all(),
    }
    return render(request, 'user/edit_user.html', context)


def user_detail(request, pk):
    user_obj = get_object_or_404(User, pk=pk)
    attendance_records = []

    if user_obj.role == 'staff':
        staff = getattr(user_obj, 'staff', None)
        if staff:
            attendance_records = Attendance.objects.filter(staff=staff).order_by('-timestamp')

    elif user_obj.role == 'student':
        student = getattr(user_obj, 'student', None)
        if student:
            attendance_records = Attendance.objects.filter(student=student).order_by('-timestamp')

    return render(request, 'user/user_detail.html', {'user_obj': user_obj, 'attendance_records': attendance_records})


@require_POST
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, f"User '{user.username}' has been deleted.")
    return redirect('user_list')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            # Restrict students and staff from logging in
            if user.role in ['student', 'staff']:
                messages.error(request, "You are not allowed to access the dashboard.")
                return redirect('login')

            # Log the user in first to create a session
            login(request, user)

            if user.role == 'school_admin':
                try:
                    school_admin = SchoolAdmin.objects.get(user=user)
                    request.session['school_id'] = school_admin.school.id
                except SchoolAdmin.DoesNotExist:
                    messages.error(request, "No school assigned to your account. Please contact the administrator.")
                    logout(request)
                    return redirect('login')
            else:
                # Remove school_id from session if any
                request.session.pop('school_id', None)

            return redirect('dashboard')

        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# Attendance management views
def add_attendance(request, user_pk):
    user_obj = get_object_or_404(User, pk=user_pk)

    if request.method == 'POST':
        date_str = request.POST.get('date')
        arrival_str = request.POST.get('arrival_time')
        departure_str = request.POST.get('departure_time')
        status = request.POST.get('status')

        try:
            arrival_time = datetime.strptime(f"{date_str} {arrival_str}", "%Y-%m-%d %H:%M")
            departure_time = datetime.strptime(f"{date_str} {departure_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            return HttpResponseBadRequest("Invalid date/time format.")

        if user_obj.role == 'student':
            try:
                student = user_obj.student
                attendance = Attendance(
                    attendee_type='student',
                    student=student,
                    school=student.school,
                    student_class=student.student_class,
                    arrival_time=arrival_time,
                    departure_time=departure_time,
                    status=status
                )
            except Student.DoesNotExist:
                return HttpResponseBadRequest("Student profile not found.")

        elif user_obj.role == 'staff':
            try:
                staff = user_obj.staff
                attendance = Attendance(
                    attendee_type='staff',
                    staff=staff,
                    school=staff.school,
                    department=staff.department,
                    arrival_time=arrival_time,
                    departure_time=departure_time,
                    status=status
                )
            except Staff.DoesNotExist:
                return HttpResponseBadRequest("Staff profile not found.")
        else:
            return HttpResponseBadRequest("Attendance can only be added for staff or student.")

        attendance.save()
        return redirect('user_detail', pk=user_obj.pk)

    return render(request, 'attendance/add_attendance.html', {'user_obj': user_obj})


def edit_attendance(request, user_pk, att_pk):
    user_obj = get_object_or_404(User, pk=user_pk)
    attendance = get_object_or_404(Attendance, pk=att_pk)

    if request.method == 'POST':
        date_str = request.POST.get('date')
        arrival_time_str = request.POST.get('arrival_time')
        departure_time_str = request.POST.get('departure_time')
        status = request.POST.get('status')

        date_obj = parse_date(date_str)
        arrival_time_obj = parse_time(arrival_time_str)
        departure_time_obj = parse_time(departure_time_str)

        if date_obj and arrival_time_obj:
            attendance.arrival_time = datetime.combine(date_obj, arrival_time_obj)
        if date_obj and departure_time_obj:
            attendance.departure_time = datetime.combine(date_obj, departure_time_obj)

        attendance.status = status
        attendance.save()
        messages.success(request, "Attendance record updated.")
        return redirect('user_detail', pk=user_pk)

    return render(request, 'attendance/edit_attendance.html', {'user_obj': user_obj, 'attendance': attendance})


def delete_attendance(request, user_pk, att_pk):
    attendance = get_object_or_404(Attendance, pk=att_pk)
    attendance.delete()
    messages.success(request, "Attendance record deleted.")
    return redirect('user_detail', pk=user_pk)
