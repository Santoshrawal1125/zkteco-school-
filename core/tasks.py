# attendance/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Student, Staff, Attendance


@shared_task
def mark_absentees():
    now = timezone.now()
    print(f"Task running at {now} (timezone-aware: {now.tzinfo})")
    today = timezone.localdate()
    students = Student.objects.all()
    staff_members = Staff.objects.all()

    for student in students:
        if not Attendance.objects.filter(student=student, timestamp__date=today).exists():
            Attendance.objects.create(student=student, status='Absent', timestamp=timezone.now())

    for staff in staff_members:
        if not Attendance.objects.filter(staff=staff, timestamp__date=today).exists():
            Attendance.objects.create(staff=staff, status='Absent', timestamp=timezone.now())
