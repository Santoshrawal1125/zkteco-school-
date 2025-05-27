# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import User, Staff, Student, School
#
#
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         # Get or create the default school once
#         default_school, _ = School.objects.get_or_create(
#             name="Nones"
#         )
#
#         if instance.role == 'staff':
#             Staff.objects.create(user=instance, school=default_school, staff_id=f'staff_{instance.id}')
#         elif instance.role == 'student':
#             Student.objects.create(user=instance, school=default_school, enrollment_number=f'student_{instance.id}')
#         elif instance.role == 'parent':
#             Parent.objects.create(user=instance, school=default_school)
#         elif instance.role == 'school_admin':
#             # School admin creates their own school (no default)
#             School.objects.create(user=instance, name=f'School of {instance.username}')
