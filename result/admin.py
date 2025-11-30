from django.contrib import admin
from .models import Class, Subject, Student, Result, GradeSystem

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'section']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'class_associated', 'teacher', 'created_at']
    list_filter = ['class_associated', 'created_at']
    search_fields = ['name', 'code']
    raw_id_fields = ['teacher']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'roll_number', 'current_class', 'section', 'phone', 'created_at']
    list_filter = ['current_class', 'section', 'created_at']
    search_fields = ['name', 'roll_number', 'father_name']
    raw_id_fields = ['user']

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'exam_type', 'marks_obtained', 'total_marks', 'percentage', 'grade', 'created_at']
    list_filter = ['exam_type', 'grade', 'student_class', 'created_at']
    search_fields = ['student__name', 'subject__name']
    readonly_fields = ['percentage', 'grade', 'gpa']
    raw_id_fields = ['student', 'subject', 'created_by']
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(GradeSystem)
class GradeSystemAdmin(admin.ModelAdmin):
    list_display = ['grade', 'min_percentage', 'max_percentage', 'gpa', 'description']
    list_editable = ['min_percentage', 'max_percentage', 'gpa']