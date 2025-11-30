from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Attendance Management
    path('', views.attendance_list, name='attendance_list'),
    path('take/', views.take_attendance, name='take_attendance'),
    path('take/preview/', views.take_attendance_preview, name='take_attendance_preview'),
    path('save/', views.save_attendance, name='save_attendance'),
    path('bulk/', views.bulk_attendance, name='bulk_attendance'),
    
    # Attendance Views
    path('detail/<int:attendance_id>/', views.attendance_detail, name='attendance_detail'),
    path('edit/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
    
    # Student Attendance
    path('my-attendance/', views.my_attendance, name='my_attendance'),
    path('report/', views.attendance_report, name='attendance_report'),
    
    # Class Reports
    path('class/<int:class_id>/summary/', views.class_attendance_summary, name='class_attendance_summary'),
    
    # API Endpoints
    path('api/students-by-class/', views.get_students_by_class, name='get_students_by_class'),
]