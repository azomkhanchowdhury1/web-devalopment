from django.contrib import admin
from .models import Teacher, ClassSchedule, Assignment, Attendance, StudentResult, Notice

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'email', 'phone', 'joining_date', 'is_active']
    list_filter = ['subject', 'is_active', 'joining_date']
    search_fields = ['name', 'email', 'phone']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('ব্যক্তিগত তথ্য', {
            'fields': ('user', 'name', 'email', 'phone', 'address', 'photo')
        }),
        ('পেশাগত তথ্য', {
            'fields': ('subject', 'joining_date', 'salary', 'qualification', 'experience')
        }),
        ('স্ট্যাটাস', {
            'fields': ('is_active',)
        }),
        ('টাইমস্ট্যাম্প', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'class_name', 'subject', 'day', 'start_time', 'end_time', 'room']
    list_filter = ['day', 'class_name', 'subject']
    search_fields = ['teacher__name', 'class_name', 'subject']
    ordering = ['day', 'start_time']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'class_name', 'subject', 'due_date', 'total_marks']
    list_filter = ['class_name', 'subject', 'due_date']
    search_fields = ['title', 'teacher__name', 'class_name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'class_name', 'subject', 'date', 'total_students', 'present_students', 'absent_students']
    list_filter = ['class_name', 'subject', 'date']
    search_fields = ['teacher__name', 'class_name']
    # readonly_fields = ['created_at']

@admin.register(StudentResult)
class StudentResultAdmin(admin.ModelAdmin):
    list_display = ['student_name', 'student_roll', 'class_name', 'subject', 'exam_type', 'marks', 'total_marks', 'grade']
    list_filter = ['class_name', 'subject', 'exam_type', 'grade']
    search_fields = ['student_name', 'student_roll', 'class_name']
    readonly_fields = ['created_at']

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'priority', 'target_class', 'is_published', 'created_at']
    list_filter = ['priority', 'is_published', 'created_at']
    search_fields = ['title', 'teacher__name', 'target_class']
    list_editable = ['is_published']
    readonly_fields = ['created_at', 'updated_at']