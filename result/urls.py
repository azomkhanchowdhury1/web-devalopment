from django.urls import path
from . import views

urlpatterns = [
    # Result management URLs
    path('', views.results_dashboard, name='results_dashboard'),
    path('enter/', views.enter_result, name='enter_result'),
    path('edit/<int:result_id>/', views.edit_result, name='edit_result'),
    path('delete/<int:result_id>/', views.delete_result, name='delete_result'),
    path('detail/<int:result_id>/', views.result_detail, name='result_detail'),
    
    # Student results
    path('my-results/', views.my_results, name='my_results'),
    
    # Bulk operations
    path('bulk-upload/', views.bulk_upload_results, name='bulk_result_upload'),
    path('download-template/', views.download_result_template, name='result_template'),
    
    # Grade system
    path('grade-system/', views.manage_grade_system, name='grade_system'),
    
    # API endpoints
    path('api/students-by-class/', views.get_students_by_class, name='students_by_class'),
    path('api/subjects-by-class/', views.get_subjects_by_class, name='subjects_by_class'),
]