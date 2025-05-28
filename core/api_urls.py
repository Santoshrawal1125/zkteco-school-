from django.urls import path
from .api_views import StaffBySchoolDepartment, DepartmentBySchool, SchoolView, StudentClassView, StudentView, \
    AttendanceView, SchoolSummaryView, update_fcm_token, MyTokenObtainPairView

urlpatterns = [
    path('school/<int:school_id>/department/<int:department_id>/staff/', StaffBySchoolDepartment.as_view(),
         name='staff-by-department'),

    path('school/<int:school_id>/department/<int:department_id>/staff/<int:staff_id>/',
         StaffBySchoolDepartment.as_view(),
         name='staff-id-by-department'),

    path('school/<int:school_id>/department/', DepartmentBySchool.as_view(), name='department-by-school'),

    path('school/', SchoolView.as_view(), name='schools-list'),

    path('school/<int:school_id>/', SchoolView.as_view(), name='schools-by-id'),

    path('school/<int:school_id>/class/', StudentClassView.as_view(), name='class-list'),

    path('school/<int:school_id>/class/<int:class_id>/student/', StudentView.as_view(), name='class-list'),

    path('school/<int:school_id>/summary/', SchoolSummaryView.as_view(), name='class-list'),

    path('school/<int:school_id>/class/<int:class_id>/student/<int:student_id>/', StudentView.as_view(),
         name='class-list'),

    path('school/<int:school_id>/department/<int:department_id>/staff/<int:staff_id>/attendance/',
         AttendanceView.as_view(),
         name='attendance-staff'),

    path('update-fcm-token/', update_fcm_token, name='update_fcm_token'),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

]
