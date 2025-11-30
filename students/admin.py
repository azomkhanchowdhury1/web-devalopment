from django.contrib import admin
from .models import Student, Guardian, Grade, Fee, Document, AcademicHistory, Attendance


class GuardianAdmin(admin.ModelAdmin):
    list_display = ['name', 'relation', 'phone', 'email']
    list_filter = ['relation']
    search_fields = ['name', 'phone', 'email']
    list_per_page = 20


class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'capacity', 'student_count', 'available_seats']
    list_filter = ['name']
    search_fields = ['name', 'section']
    
    def student_count(self, obj):
        return obj.student_count()
    student_count.short_description = 'শিক্ষার্থী সংখ্যা'
    
    def available_seats(self, obj):
        return obj.available_seats()
    available_seats.short_description = 'খালি আসন'


class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'full_name', 'grade', 'gender', 'status', 'admission_date']
    list_filter = ['grade', 'gender', 'status', 'admission_date']
    search_fields = ['first_name', 'last_name', 'roll_number', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    
    fieldsets = (
        ('ব্যক্তিগত তথ্য', {
            'fields': ('first_name', 'last_name', 'roll_number', 'date_of_birth', 'gender', 'blood_group', 'photo')
        }),
        ('শিক্ষাগত তথ্য', {
            'fields': ('grade', 'admission_date', 'status')
        }),
        ('যোগাযোগের তথ্য', {
            'fields': ('address', 'district', 'phone', 'email')
        }),
        ('অভিভাবকের তথ্য', {
            'fields': ('guardian',)
        }),
        ('সিস্টেম তথ্য', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def full_name(self, obj):
        return obj.full_name()
    full_name.short_description = 'পূর্ণ নাম'
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


class FeeAdmin(admin.ModelAdmin):
    list_display = ['student', 'month', 'year', 'amount', 'paid_amount', 'due_amount', 'status', 'due_date']
    list_filter = ['month', 'year', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'student__roll_number']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 25
    
    def due_amount(self, obj):
        return obj.due_amount()
    due_amount.short_description = 'বাকি পরিমাণ'


class DocumentAdmin(admin.ModelAdmin):
    list_display = ['student', 'document_type', 'title', 'issue_date', 'uploaded_at']
    list_filter = ['document_type', 'issue_date']
    search_fields = ['student__first_name', 'student__last_name', 'title']
    readonly_fields = ['uploaded_at']
    list_per_page = 25


class AcademicHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'academic_year', 'grade', 'section', 'roll_number', 'result', 'status']
    list_filter = ['academic_year', 'grade', 'status']
    search_fields = ['student__first_name', 'student__last_name', 'academic_year']
    readonly_fields = ['created_at']
    list_per_page = 25


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'status', 'marked_by', 'marked_at']
    list_filter = ['date', 'status']
    search_fields = ['student__first_name', 'student__last_name']
    readonly_fields = ['marked_at']
    list_per_page = 25


admin.site.register(Guardian, GuardianAdmin)
admin.site.register(Grade, GradeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Fee, FeeAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(AcademicHistory, AcademicHistoryAdmin)
admin.site.register(Attendance, AttendanceAdmin)