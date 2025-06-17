#!/usr/bin/env python
#AS OUR HOSTED PLATFORM DIDINT SUPPORT SUDO FOR SUPERVISIOR OF REDIS AND CELERY WE NEED TO USE THIS FRO CRON JOB.
import os
import sys
import django
from django.utils import timezone

# Set up Django environment to access models
sys.path.append('/home/alsamain/attendance.alsamainternational.com')  # your project root path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendence.settings')  # Change 'attendence' to your project name
django.setup()

from core.models import Student, Staff, Attendance


def mark_absentees():
    now = timezone.now()
    print(f"Running mark_absentees at {now} (timezone: {now.tzinfo})")
    today = timezone.localdate()

    students = Student.objects.all()
    staff_members = Staff.objects.all()

    for student in students:
        if not Attendance.objects.filter(student=student, timestamp__date=today).exists():
            Attendance.objects.create(student=student, status='Absent', timestamp=now)

    for staff in staff_members:
        if not Attendance.objects.filter(staff=staff, timestamp__date=today).exists():
            Attendance.objects.create(staff=staff, status='Absent', timestamp=now)


if __name__ == '__main__':
    mark_absentees()
