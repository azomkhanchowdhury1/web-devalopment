from django.contrib import admin
from .models import AcademicYear, Subject, Class, ClassSubject, ClassRoutine

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ['year', 'start_date', 'end_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['year']
    ordering = ['-year']
    actions = ['make_active']

    def make_active(self, request, queryset):
        # Deactivate all academic years first
        AcademicYear.objects.filter(is_active=True).update(is_active=False)
        # Activate selected ones
        queryset.update(is_active=True)
        self.message_user(request, "Selected academic years have been activated.")
    make_active.short_description = "Activate selected academic years"

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'subject_type', 'credit_hours', 'is_active']
    list_filter = ['subject_type', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['name']

class ClassSubjectInline(admin.TabularInline):
    model = ClassSubject
    extra = 1
    raw_id_fields = ['teacher']

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'class_teacher', 'academic_year', 'capacity', 'student_count', 'is_active']
    list_filter = ['academic_year', 'is_active']
    search_fields = ['name', 'section', 'room_number']
    raw_id_fields = ['class_teacher']
    inlines = [ClassSubjectInline]
    
    def student_count(self, obj):
        return obj.student_set.count()
    student_count.short_description = 'Students'

@admin.register(ClassRoutine)
class ClassRoutineAdmin(admin.ModelAdmin):
    list_display = ['class_obj', 'day', 'period', 'subject', 'teacher', 'start_time', 'end_time', 'is_active']
    list_filter = ['class_obj', 'day', 'is_active']
    search_fields = ['class_obj__name', 'subject__name', 'teacher__username']
    ordering = ['class_obj', 'day', 'period']
    raw_id_fields = ['teacher']

# Register ClassSubject separately if needed
@admin.register(ClassSubject)
class ClassSubjectAdmin(admin.ModelAdmin):
    list_display = ['class_obj', 'subject', 'teacher', 'is_compulsory']
    list_filter = ['class_obj', 'is_compulsory']
    search_fields = ['class_obj__name', 'subject__name']
    raw_id_fields = ['teacher']