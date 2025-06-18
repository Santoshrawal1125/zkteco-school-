import os
import sys
import django
from django.utils import timezone

# 👇 Add this to include the project root directory in sys.path
sys.path.append('D:/attendance.alsamainternational.com')

# Set the settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "attendence.settings")
django.setup()

from core.models import Student, Staff, Attendance, Holiday


def mark_absentees():
    today = timezone.localdate()
    now = timezone.now()

    students = Student.objects.select_related('school').all()
    staff_members = Staff.objects.select_related('school').all()

    for student in students:
        school = student.school
        is_holiday = Holiday.objects.filter(
            school=school,
            start_date__lte=today,
            end_date__gte=today
        ).exists()
        if is_holiday:
            continue

        if not Attendance.objects.filter(student=student, timestamp__date=today).exists():
            Attendance.objects.create(student=student, status='Absent', timestamp=now)

    for staff in staff_members:
        school = staff.school
        is_holiday = Holiday.objects.filter(
            school=school,
            start_date__lte=today,
            end_date__gte=today
        ).exists()
        if is_holiday:
            continue

        if not Attendance.objects.filter(staff=staff, timestamp__date=today).exists():
            Attendance.objects.create(staff=staff, status='Absent', timestamp=now)


mark_absentees()
