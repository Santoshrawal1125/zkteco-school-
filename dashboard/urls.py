from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('attendance/', views.attendance, name='attendance'),
    path('student/', views.student_attendance, name='student_attendance'),
    path('staff/', views.staff_attendance, name='staff_attendance'),

#school and its related pages 
    path('school/', views.school, name='school'),
    path('add_school/', views.add_school, name='add_school'),
    path('school_details/<int:pk>/', views.school_details, name='school_details'),
    path('school_delete/<int:pk>/', views.school_delete, name='school_delete'),
#departments and its related pages
    path('departments/', views.departments, name='departments'),
    path('school/<int:school_id>/departments/', views.school_departments, name='school_departments'),
    
#devices and its related pages
    path('schools_list/', views.school_list, name='school_list'),
    path('schools/<int:school_id>/devices/', views.devices_by_school, name='devices_by_school'),

#shifts and its related pages
    path('shifts/', views.shift_list, name='shifts'),


    path('user/', views.user, name='users')
]