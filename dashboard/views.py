from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from core.models import School
from core.models import Department


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


def add_school(request):
    if request.method == "POST":
        name = request.POST.get('name')
        address = request.POST.get('address')

        if name and address:
            School.objects.create(name=name, address=address)
            return redirect('school')

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
            return redirect('school')

    return render(request, 'school/school_details.html', {'school': school})


def school_delete(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == "POST":
        school.delete()
        messages.success(request, "School has been deleted successfully.")
        return redirect('school')
    return redirect('school_details', pk=pk)


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


def user(request):
    return render(request, 'user/user.html')
