# Generated by Django 5.2.1 on 2025-05-30 09:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_staff_phone_student_guardian_phone_alter_staff_user_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='staff',
            name='phone',
        ),
        migrations.RemoveField(
            model_name='student',
            name='guardian_phone',
        ),
        migrations.AlterField(
            model_name='staff',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
