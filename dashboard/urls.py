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
    # list of student classes under a specific school
    path('school/<int:school_id>/classes/', views.school_student_classes, name='school_student_classes'),
    path('school/<int:school_id>/classes/<int:student_class_id>/student/', views.school_class_student, name='school_student_classes'),

    # departments and its related pages
    path('departments/', views.departments, name='departments'),
    path('school/<int:school_id>/departments/', views.school_departments, name='school_departments'),

    # devices and its related pages
    path('schools_list/', views.school_list, name='school_list'),
    path('schools/<int:school_id>/devices/', views.devices_by_school, name='devices_by_school'),

    # shifts and its related pages
    path('shifts/', views.shift_list, name='shifts'),
    path('shifts/<int:school_id>/', views.shift_list, name='shifts'),

    # USER
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:pk>/', views.user_detail, name='user_detail'),
    path('users/<int:pk>/delete/', views.delete_user, name='delete_user'),

    # LOGOUT
    path('logout/', views.logout_view, name='logout'),

    # attendence
    path('users/<int:user_pk>/attendance/add/', views.add_attendance, name='add_attendance'),
    path('users/<int:user_pk>/attendance/<int:att_pk>/edit/', views.edit_attendance, name='edit_attendance'),
    path('users/<int:user_pk>/attendance/<int:att_pk>/delete/', views.delete_attendance, name='delete_attendance'),

]
