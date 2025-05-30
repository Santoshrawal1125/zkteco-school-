from django.db import models
from django.contrib.auth.models import AbstractUser


# Custom User model with roles
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),  # superuser or staff user in Django admin
        ('school_admin', 'School Admin'),
        ('staff', 'Staff'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


# School created by admin (tracked by superuser, no explicit link to Admin model)
class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# School Admin for each school
class SchoolAdmin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='schooladmin')
    fcm_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.user.username


# Department in a school (for staff)
class Department(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.school.name}"


class Shift(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='shifts')
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time}) - {self.school.name}"


# Student class (e.g., Grade 10, Section A)
class StudentClass(models.Model):
    name = models.CharField(max_length=100)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.school.name}"


# Staff model
class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='staff_images/', blank=True, null=True)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    fcm_token = models.TextField(blank=True, null=True)
    shift = models.ForeignKey(Shift, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username


# Student model
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.SET_NULL, null=True)
    fcm_token = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


# ZKTeco Device linked to a school
class Device(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    serial_number = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.serial_number} - {self.school.name}"


# Unified Attendance model for staff and student
from django.utils.timezone import localtime
import datetime


class Attendance(models.Model):
    ATTENDEE_TYPE = [
        ('staff', 'Staff'),
        ('student', 'Student'),
    ]

    STATUS_CHOICES = [
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
    ]

    attendee_type = models.CharField(max_length=10, choices=ATTENDEE_TYPE)
    staff = models.ForeignKey(Staff, null=True, blank=True, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, null=True, blank=True, on_delete=models.CASCADE)

    timestamp = models.DateTimeField(auto_now_add=True)
    arrival_time = models.DateTimeField(null=True, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)

    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL)
    student_class = models.ForeignKey(StudentClass, null=True, blank=True, on_delete=models.SET_NULL)
    school = models.ForeignKey(School, null=True, blank=True, on_delete=models.SET_NULL)

    def save(self, *args, **kwargs):
        # Step 1: Get the assigned shift based on attendee type
        shift = None
        if self.attendee_type == 'staff' and self.staff and self.staff.shift:
            shift = self.staff.shift
        elif self.attendee_type == 'student' and self.student and self.student.student_class and self.student.student_class.shift:
            shift = self.student.student_class.shift

        # Step 2: Determine attendance status using shift start time
        if self.arrival_time and shift:
            # Convert arrival time to local time (server time → local time)
            local_arrival = localtime(self.arrival_time)

            # Compare arrival time with shift start time
            if local_arrival.time() > shift.start_time:
                self.status = 'late'
            else:
                self.status = 'present'
        else:
            # If arrival time is missing or shift is not set, mark as absent
            self.status = 'absent'

        # Step 3: Save the model as usual
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attendee_type} - {self.status} - {self.timestamp}"
