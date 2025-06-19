from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('attendance/', views.attendance, name='attendance'),
    path('student/', views.student_attendance, name='student_attendance'),
    path('staff/', views.staff_attendance, name='staff_attendance'),

    # school and its related pages
    path('school/', views.school, name='school'),
    path('add_school/', views.add_school, name='add_school'),
    path('school_details/<int:pk>/', views.school_details, name='school_details'),
    path('school_delete/<int:pk>/', views.school_delete, name='school_delete'),
    path('student_and_staff/<int:school_id>/', views.student_and_staff, name='student_and_staff'),
    path('student_and_staff/', views.student_and_staff, name='student_and_staff'),

    # staffs according to their school
    path('school/<int:school_id>/department/<int:department_id>/staffs/', views.school_staffs, name='school_staffs'),

    # student add
    path('school/<int:school_id>/class/<int:class_id>/students/add/', views.add_student, name='add_student'),
    path('dashboard/school/<int:school_id>/class/<int:class_id>/student/<int:student_id>/delete/', views.delete_student,
         name='delete_student'),
    path('dashboard/school/<int:school_id>/class/<int:student_class_id>/students/<int:student_id>/edit/',
         views.edit_student, name='edit_student'),

    # list of student classes under a specific school
    path('school/<int:school_id>/classes/', views.school_student_classes, name='school_student_classes'),
    path('school/<int:school_id>/classes/<int:student_class_id>/student/', views.school_class_student,
         name='school_class_student'),
    path('school/<int:school_id>/classes/add/', views.add_class, name='add_class'),
    path('school/<int:school_id>/classes/<int:class_id>/edit/', views.edit_class, name='edit_class'),
    path('school/<int:school_id>/classes/<int:class_id>/delete/', views.delete_class, name='delete_class'),

    # departments and its related pages
    path('departments/', views.departments, name='departments'),
    path('school/<int:school_id>/departments/', views.school_departments, name='school_departments'),
    path('school/<int:school_id>/departments/add/', views.add_department, name='add_department'),
    path('school/<int:school_id>/departments/<int:department_id>/edit/', views.edit_department, name='edit_department'),
    path('school/<int:school_id>/departments/<int:department_id>/delete/', views.delete_department,
         name='delete_department'),

    # devices and its related pages
    path('schools_list/', views.school_list, name='school_list'),
    path('schools/<int:school_id>/devices/', views.devices_by_school, name='devices_by_school'),
    path('school/<int:school_id>/devices/add/', views.add_device, name='add_device'),
    path('device/<int:device_id>/edit/', views.edit_device, name='edit_device'),
    path('device/<int:device_id>/delete/', views.delete_device, name='delete_device'),

    # shifts and its related pages
    path('shifts/', views.shift_list, name='shifts'),
    path('shifts/<int:school_id>/', views.shift_list, name='shifts'),
    path('shifts/add/<int:school_id>/', views.add_shift, name='add_shift'),
    path('delete/<int:id>/', views.delete_shift, name='delete_shift'),
    path('shifts/edit/<int:id>/', views.edit_shift, name='edit_shift'),

    # holidays and related pages
    path('holidays/', views.holiday_list, name='holidays'),
    path('holidays/<int:school_id>/', views.holiday_list, name='holidays'),
    path('holidays/add/<int:school_id>/', views.add_holiday, name='add_holiday'),
    path('holidays/delete/<int:id>/', views.delete_holiday, name='delete_holiday'),
    path('holidays/edit/<int:id>/', views.edit_holiday, name='edit_holiday'),

    # USER
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),

    # LOGOUT
    path('logout/', views.logout_view, name='logout'),

    # STAFF
    path('school/<int:school_id>/department/<int:department_id>/add-staff/', views.add_staff, name='add_staff'),
    path('school/<int:school_id>/staff/delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('school/<int:school_id>/staff/edit/<int:staff_id>/', views.edit_staff, name='edit_staff'),

    # attendence
    path('users/<int:user_pk>/attendance/add/', views.add_attendance, name='add_attendance'),
    path('users/<int:user_pk>/attendance/<int:att_pk>/edit/', views.edit_attendance, name='edit_attendance'),
    path('users/<int:user_pk>/attendance/<int:att_pk>/delete/', views.delete_attendance, name='delete_attendance'),

    # Schooladmin

    path('school-admins/', views.school_admin_list, name='school_admin_list'),
    path('school-admins/add/', views.add_school_admin, name='add_school_admin'),
    path('school-admins/<int:pk>/edit/', views.edit_school_admin, name='edit_school_admin'),
    path('school-admins/<int:pk>/delete/', views.delete_school_admin, name='delete_school_admin'),

]
