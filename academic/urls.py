from django.urls import path
from . import views

app_name = 'academic'

urlpatterns = [
    # Academic Year URLs
    path('academic-years/', views.academic_year_list, name='academic_year_list'),
    path('academic-years/create/', views.academic_year_create, name='academic_year_create'),
    path('academic-years/<int:pk>/edit/', views.academic_year_edit, name='academic_year_edit'),
    path('academic-years/<int:pk>/delete/', views.academic_year_delete, name='academic_year_delete'),
    
    # Subject URLs
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/create/', views.subject_create, name='subject_create'),
    path('subjects/<int:pk>/edit/', views.subject_edit, name='subject_edit'),
    path('subjects/<int:pk>/delete/', views.subject_delete, name='subject_delete'),
    
    # Class URLs
    path('classes/', views.class_list, name='class_list'),
    path('classes/create/', views.class_create, name='class_create'),
    path('classes/<int:pk>/edit/', views.class_edit, name='class_edit'),
    path('classes/<int:pk>/delete/', views.class_delete, name='class_delete'),
    path('classes/<int:pk>/', views.class_detail, name='class_detail'),
    
    # Routine URLs
    path('routines/', views.routine_list, name='routine_list'),
    path('routines/create/', views.routine_create, name='routine_create'),
    path('routines/<int:pk>/edit/', views.routine_edit, name='routine_edit'),
    path('routines/<int:pk>/delete/', views.routine_delete, name='routine_delete'),
    path('api/class-routine/<int:class_id>/', views.get_class_routine, name='get_class_routine'),
]