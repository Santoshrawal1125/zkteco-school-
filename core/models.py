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
    phone_number = models.CharField(max_length=10, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.full_clean()  # This triggers field validation
        super().save(*args, **kwargs)


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


from django.utils.timezone import make_aware, is_naive, localtime


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
    review = models.CharField(max_length=500, blank=True, null=True)
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
            # Make sure arrival_time is timezone-aware
            if is_naive(self.arrival_time):
                self.arrival_time = make_aware(self.arrival_time)

            local_arrival = localtime(self.arrival_time)

            if local_arrival.time() > shift.start_time:
                self.status = 'late'
            else:
                self.status = 'present'
        else:
            self.status = 'absent'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.attendee_type} - {self.status} - {self.timestamp}"


# models.py

class Holiday(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)

    # Use start_date and end_date to support single or multi-day holidays
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        if self.start_date == self.end_date:
            return f"{self.school.name} - {self.start_date} ({self.name})"
        return f"{self.school.name} - {self.start_date} to {self.end_date} ({self.name})"

    class Meta:
        verbose_name = "Holiday"
        verbose_name_plural = "Holidays"

