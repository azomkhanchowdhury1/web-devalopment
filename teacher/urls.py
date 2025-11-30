from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.teacher_register, name='teacher_register'),
    path('login/', views.teacher_login, name='teacher_login'),
    path('logout/', views.teacher_logout, name='teacher_logout'),
    
    # Teacher Profile URLs
    path('profile/', views.teacher_profile, name='teacher_profile'),
    path('profile/edit/', views.edit_teacher_profile, name='edit_teacher_profile'),
    
    # Dashboard and Portal URLs
    path('dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('portal/', views.teacher_portal, name='teacher_portal'),
    
    # Teacher Management URLs
    path('list/', views.teacher_list, name='teacher_list'),
    path('add/', views.add_teacher, name='add_teacher'),
    path('detail/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    path('edit/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('delete/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    
    # Class Schedule URLs
    path('schedule/', views.class_schedule_list, name='class_schedule_list'),
    path('schedule/add/', views.add_class_schedule, name='add_class_schedule'),
    path('schedule/edit/<int:schedule_id>/', views.edit_class_schedule, name='edit_class_schedule'),
    path('schedule/delete/<int:schedule_id>/', views.delete_class_schedule, name='delete_class_schedule'),
    
    # Assignment URLs
    path('assignments/', views.assignment_list, name='assignment_list'),
    path('assignments/add/', views.add_assignment, name='add_assignment'),
    path('assignments/detail/<int:assignment_id>/', views.assignment_detail, name='assignment_detail'),
    path('assignments/edit/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('assignments/delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    
    # Attendance URLs
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/add/', views.add_attendance, name='add_attendance'),
    path('attendance/edit/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
    path('attendance/delete/<int:attendance_id>/', views.delete_attendance, name='delete_attendance'),
    
    # Result URLs
    path('results/', views.result_list, name='result_list'),
    path('results/add/', views.add_result, name='add_result'),
    path('results/edit/<int:result_id>/', views.edit_result, name='edit_result'),
    path('results/delete/<int:result_id>/', views.delete_result, name='delete_result'),
    path('results/upload/', views.upload_results, name='upload_results'),
    
    # Notice URLs
    path('notices/', views.notice_list, name='notice_list'),
    path('notices/add/', views.add_notice, name='add_notice'),
    path('notices/edit/<int:notice_id>/', views.edit_notice, name='edit_notice'),
    path('notices/delete/<int:notice_id>/', views.delete_notice, name='delete_notice'),
    
    # API URLs for AJAX
    path('api/teacher-stats/', views.teacher_stats_api, name='teacher_stats_api'),
    path('api/today-schedule/', views.today_schedule_api, name='today_schedule_api'),
]