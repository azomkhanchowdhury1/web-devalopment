from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count
from .models import AttendanceRecord, MonthlyReport
from datetime import datetime

@receiver(post_save, sender=AttendanceRecord)
def update_monthly_report(sender, instance, created, **kwargs):
    if created:
        attendance = instance.attendance
        student = instance.student
        month = attendance.date.month
        year = attendance.date.year
        
        # Get or create monthly report
        monthly_report, created = MonthlyReport.objects.get_or_create(
            student=student,
            month=month,
            year=year,
            defaults={
                'total_days': 0,
                'present_days': 0,
                'absent_days': 0,
                'late_days': 0,
            }
        )
        
        # Update counts
        monthly_report.total_days = AttendanceRecord.objects.filter(
            student=student,
            attendance__date__month=month,
            attendance__date__year=year
        ).count()
        
        monthly_report.present_days = AttendanceRecord.objects.filter(
            student=student,
            attendance__date__month=month,
            attendance__date__year=year,
            status='present'
        ).count()
        
        monthly_report.absent_days = AttendanceRecord.objects.filter(
            student=student,
            attendance__date__month=month,
            attendance__date__year=year,
            status='absent'
        ).count()
        
        monthly_report.late_days = AttendanceRecord.objects.filter(
            student=student,
            attendance__date__month=month,
            attendance__date__year=year,
            status='late'
        ).count()
        
        monthly_report.save()