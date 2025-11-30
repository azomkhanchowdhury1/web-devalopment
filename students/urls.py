from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    # Student URLs
    path('', views.StudentListView.as_view(), name='student_list'),
    path('add/', views.StudentCreateView.as_view(), name='student_add'),
    path('<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student_edit'),
    path('<int:pk>/delete/', views.StudentDeleteView.as_view(), name='student_delete'),
    
    # Guardian URLs
    path('<int:student_id>/guardian/edit/', views.GuardianUpdateView.as_view(), name='guardian_edit'),
    
    # Fee URLs
    path('fees/', views.FeeListView.as_view(), name='fee_list'),
    path('fees/add/', views.FeeCreateView.as_view(), name='fee_add'),
    path('fees/<int:pk>/edit/', views.FeeUpdateView.as_view(), name='fee_edit'),
    path('fees/<int:pk>/delete/', views.FeeDeleteView.as_view(), name='fee_delete'),
    
    # Document URLs
    path('<int:student_id>/documents/add/', views.DocumentCreateView.as_view(), name='document_add'),
    path('documents/<int:pk>/delete/', views.DocumentDeleteView.as_view(), name='document_delete'),
    
    # Academic History URLs
    path('<int:student_id>/academic-history/add/', views.AcademicHistoryCreateView.as_view(), name='academic_history_add'),
    
    # Bulk Operations
    path('bulk-upload/', views.BulkUploadView.as_view(), name='bulk_upload'),
    path('promote/', views.PromoteStudentsView.as_view(), name='promote_students'),
    
    # Student Portal
    path('portal/', views.StudentPortalView.as_view(), name='student_portal'),
    
    # Statistics and Reports
    path('statistics/', views.StudentStatisticsView.as_view(), name='student_statistics'),
    
    # API URLs for AJAX
    path('api/students-by-grade/', views.get_students_by_grade, name='api_students_by_grade'),
    path('api/student-counts/', views.get_student_counts, name='api_student_counts'),
]