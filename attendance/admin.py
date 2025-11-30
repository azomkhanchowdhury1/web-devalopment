from django.contrib import admin
from .models import Class, Subject, Student, Attendance, AttendanceRecord, MonthlyReport

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['class_name', 'section', 'get_student_count']
    list_filter = ['class_name', 'section']
    search_fields = ['class_name', 'section']
    
    def get_student_count(self, obj):
        return obj.student_set.count()
    get_student_count.short_description = 'মোট শিক্ষার্থী'

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code']
    search_fields = ['name', 'code']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'roll_number', 'name', 'class_info', 'gender', 'is_active']
    list_filter = ['class_info', 'gender', 'is_active']
    search_fields = ['student_id', 'name', 'roll_number', 'guardian_name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('ব্যক্তিগত তথ্য', {
            'fields': ('student_id', 'roll_number', 'name', 'gender', 'date_of_birth', 'photo')
        }),
        ('শ্রেণী তথ্য', {
            'fields': ('class_info',)
        }),
        ('যোগাযোগ তথ্য', {
            'fields': ('address', 'phone', 'email')
        }),
        ('অভিভাবক তথ্য', {
            'fields': ('guardian_name', 'guardian_phone')
        }),
        ('স্ট্যাটাস', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )

class AttendanceRecordInline(admin.TabularInline):
    model = AttendanceRecord
    extra = 0
    readonly_fields = ['created_at']
    fields = ['student', 'status', 'remarks', 'created_at']
    can_delete = False

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['class_info', 'subject', 'date', 'period', 'teacher', 'total_students', 'present_count', 'attendance_percentage']
    list_filter = ['class_info', 'subject', 'date', 'teacher']
    search_fields = ['class_info__class_name', 'subject__name', 'date']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AttendanceRecordInline]
    
    def total_students(self, obj):
        return obj.total_students
    total_students.short_description = 'মোট শিক্ষার্থী'
    
    def present_count(self, obj):
        return obj.present_count
    present_count.short_description = 'উপস্থিত'
    
    def attendance_percentage(self, obj):
        return f"{obj.attendance_percentage}%"
    attendance_percentage.short_description = 'উপস্থিতির হার'

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['student', 'attendance', 'status', 'remarks', 'created_at']
    list_filter = ['status', 'attendance__date', 'attendance__class_info']
    search_fields = ['student__name', 'student__roll_number', 'attendance__subject__name']
    readonly_fields = ['created_at']

@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'month', 'year', 'total_days', 'present_days', 'attendance_percentage']
    list_filter = ['month', 'year', 'student__class_info']
    search_fields = ['student__name', 'student__roll_number']
    readonly_fields = ['attendance_percentage']