from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import *
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from core.models import StudentClass


# Create your views here.
def dashboard(request):
    return render(request, 'base/admin_base.html')


def attendance(request):
    return render(request, 'attendance/attendance.html')


def student_attendance(request):
    return render(request, 'attendance/student_attendance.html')


def staff_attendance(request):
    return render(request, 'attendance/staff_attendance.html')


# school and its related pages
def school(request):
    schools = School.objects.all()
    return render(request, 'school/school.html', {'schools': schools})


from django.contrib import messages  # Add this import at the top


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



def student_and_staff(request, school_id):
    school = get_object_or_404(School, id=school_id)
    return render(request, 'school/studentandstaff.html', {'school': school})

#staff according to their school

def school_staffs(request, school_id):
    school = get_object_or_404(School, id=school_id)
    staffs = Staff.objects.filter(school=school)

    return render(request, 'school/staff_acc_to_school.html', {
        'school': school,
        'staffs': staffs,
    })

    #list of student classes under a specific school
def school_student_classes(request, school_id):
    school = get_object_or_404(School, id=school_id)
    student_classes = StudentClass.objects.filter(school=school)

    return render(request, 'school/school_classes.html', {
        'school': school,
        'student_classes': student_classes,
    })



# department and theire pages
def departments(request):
    departments = Department.objects.select_related('school').all()
    schools = School.objects.all()

    return render(request, 'departments/departments.html', {
        'departments': departments,
        'schools': schools
    })


def school_departments(request, school_id):
    school = get_object_or_404(School, id=school_id)
    departments = Department.objects.filter(school=school)

    return render(request, 'departments/school_departments.html', {
        'school': school,
        'departments': departments,
    })


# device and their pages
def school_list(request):
    schools = School.objects.all()
    return render(request, 'device/school_list.html', {'schools': schools})


def devices_by_school(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    devices = Device.objects.filter(school=school)
    return render(request, 'device/devices_by_school.html', {
        'school': school,
        'devices': devices
    })


# shift and their pages


def shift_list(request):
    shifts = Shift.objects.select_related('school').all().order_by('school__name', 'start_time')
    return render(request, 'shift/shift_list.html', {'shifts': shifts})


User = get_user_model()


def user_list(request):
    users = User.objects.all()
    return render(request, 'user/user_list.html', {'users': users})


def add_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')

        if role == 'student':
            password = f"{username}@123"  # Auto-generated password for student
        else:
            password = request.POST.get('password')

        school_id = request.POST.get('school')
        school = School.objects.filter(id=school_id).first()

        user = User.objects.create_user(username=username, email=email, password=password, role=role)

        if role == 'school_admin':
            SchoolAdmin.objects.create(user=user, school=school)
        elif role == 'staff':
            department_id = request.POST.get('department')
            position = request.POST.get('position')
            shift_id = request.POST.get('shift')
            Staff.objects.create(user=user, school=school, department_id=department_id,
                                 position=position, shift_id=shift_id)
        elif role == 'student':
            student_class_id = request.POST.get('student_class')
            Student.objects.create(user=user, school=school, student_class_id=student_class_id)

        # ✅ Place this block here:
        if role == 'student':
            messages.success(request, f"Student user added successfully. Default password is: {password}")
        elif role == 'staff':
            messages.success(request, f"Staff user added successfully. Default password is: {password}")
        else:
            messages.success(request, 'User added successfully.')

        return redirect('user_list')  # after success message

    # for GET request
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

        # Update role-specific data if needed (optional)
        messages.success(request, 'User updated successfully.')
        return redirect('user_list')

    context = {
        'user_obj': user,
        'schools': School.objects.all(),
    }
    return render(request, 'user/edit_user.html', context)


def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'user/user_detail.html', {'user_obj': user})


@require_POST
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    messages.success(request, f"User '{user.username}' has been deleted.")
    return redirect('user_list')


#LOGIN VIEW

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login/login.html')

#LOG OUT VIEW

def logout_view(request):
    logout(request)
    return redirect('login')
