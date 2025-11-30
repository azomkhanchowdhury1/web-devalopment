from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from datetime import datetime, date
import calendar

from .models import Attendance, AttendanceRecord, Student, Class, Subject, MonthlyReport
from .forms import AttendanceForm, AttendanceFilterForm, StudentAttendanceFilterForm, BulkAttendanceForm

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists() or user.is_staff

@login_required
def attendance_list(request):
    attendances = Attendance.objects.all().order_by('-date', '-created_at')
    
    form = AttendanceFilterForm(request.GET)
    if form.is_valid():
        class_name = form.cleaned_data.get('class_name')
        section = form.cleaned_data.get('section')
        attendance_date = form.cleaned_data.get('date')
        subject = form.cleaned_data.get('subject')
        
        if class_name:
            attendances = attendances.filter(class_info__class_name=class_name)
        if section:
            attendances = attendances.filter(class_info__section=section)
        if attendance_date:
            attendances = attendances.filter(date=attendance_date)
        if subject:
            attendances = attendances.filter(subject=subject)
    
    # Pagination
    paginator = Paginator(attendances, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'attendances': page_obj,
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'attendance/attendance_list.html', context)

@login_required
@user_passes_test(is_teacher)
def take_attendance(request):
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            # Store in session for preview
            request.session['attendance_data'] = {
                'class_info_id': form.cleaned_data['class_info'].id,
                'subject_id': form.cleaned_data['subject'].id,
                'date': form.cleaned_data['date'].isoformat(),
                'period': form.cleaned_data['period'],
            }
            return redirect('attendance:take_attendance_preview')
    else:
        form = AttendanceForm()
    
    context = {
        'form': form,
    }
    return render(request, 'attendance/take_attendance.html', context)

@login_required
@user_passes_test(is_teacher)
def take_attendance_preview(request):
    attendance_data = request.session.get('attendance_data')
    if not attendance_data:
        messages.error(request, 'দয়া করে প্রথমে উপস্থিতির তথ্য নির্বাচন করুন')
        return redirect('attendance:take_attendance')
    
    try:
        class_info = Class.objects.get(id=attendance_data['class_info_id'])
        subject = Subject.objects.get(id=attendance_data['subject_id'])
        students = Student.objects.filter(class_info=class_info, is_active=True).order_by('roll_number')
        
        # Check if attendance already exists
        existing_attendance = Attendance.objects.filter(
            class_info=class_info,
            subject=subject,
            date=attendance_data['date'],
            period=attendance_data['period']
        ).first()
        
        if existing_attendance:
            messages.warning(request, 'এই শ্রেণী, বিষয়, তারিখ এবং পিরিয়ডের জন্য ইতিমধ্যেই উপস্থিতি নেওয়া হয়েছে')
            return redirect('attendance:attendance_detail', attendance_id=existing_attendance.id)
        
    except (Class.DoesNotExist, Subject.DoesNotExist):
        messages.error(request, 'অবৈধ শ্রেণী বা বিষয় নির্বাচন করা হয়েছে')
        return redirect('attendance:take_attendance')
    
    context = {
        'class_info': class_info,
        'subject': subject,
        'date': attendance_data['date'],
        'period': attendance_data['period'],
        'students': students,
    }
    return render(request, 'attendance/take_attendance_preview.html', context)

@login_required
@user_passes_test(is_teacher)
def save_attendance(request):
    if request.method != 'POST':
        return redirect('attendance:take_attendance')
    
    attendance_data = request.session.get('attendance_data')
    if not attendance_data:
        messages.error(request, 'দয়া করে প্রথমে উপস্থিতির তথ্য নির্বাচন করুন')
        return redirect('attendance:take_attendance')
    
    try:
        class_info = Class.objects.get(id=attendance_data['class_info_id'])
        subject = Subject.objects.get(id=attendance_data['subject_id'])
        students = Student.objects.filter(class_info=class_info, is_active=True)
        
        # Create attendance record
        attendance = Attendance.objects.create(
            class_info=class_info,
            subject=subject,
            date=attendance_data['date'],
            period=attendance_data['period'],
            teacher=request.user
        )
        
        # Create attendance records for each student
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'present')
            remarks = request.POST.get(f'remarks_{student.id}', '')
            
            AttendanceRecord.objects.create(
                attendance=attendance,
                student=student,
                status=status,
                remarks=remarks
            )
        
        # Clear session data
        if 'attendance_data' in request.session:
            del request.session['attendance_data']
        
        messages.success(request, f'{class_info} শ্রেণীর জন্য উপস্থিতি সফলভাবে সংরক্ষণ করা হয়েছে')
        return redirect('attendance:attendance_detail', attendance_id=attendance.id)
        
    except Exception as e:
        messages.error(request, f'উপস্থিতি সংরক্ষণ করতে সমস্যা হয়েছে: {str(e)}')
        return redirect('attendance:take_attendance')

@login_required
def attendance_detail(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id)
    attendance_records = attendance.attendance_records.select_related('student').all()
    
    context = {
        'attendance': attendance,
        'attendance_details': attendance_records,
    }
    return render(request, 'attendance/attendance_detail.html', context)

@login_required
@user_passes_test(is_teacher)
def edit_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id)
    attendance_records = attendance.attendance_records.select_related('student').all()
    
    if request.method == 'POST':
        for record in attendance_records:
            status = request.POST.get(f'status_{record.student.id}')
            remarks = request.POST.get(f'remarks_{record.student.id}', '')
            
            if status in ['present', 'absent', 'late', 'excused']:
                record.status = status
                record.remarks = remarks
                record.save()
        
        messages.success(request, 'উপস্থিতি সফলভাবে আপডেট করা হয়েছে')
        return redirect('attendance:attendance_detail', attendance_id=attendance.id)
    
    context = {
        'attendance': attendance,
        'attendance_details': attendance_records,
    }
    return render(request, 'attendance/edit_attendance.html', context)

@login_required
def my_attendance(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'আপনি একজন শিক্ষার্থী নন')
        return redirect('dashboard')
    
    student = request.user.student
    attendance_records = AttendanceRecord.objects.filter(
        student=student
    ).select_related('attendance', 'attendance__subject', 'attendance__class_info').order_by('-attendance__date')
    
    # Calculate statistics
    total_classes = attendance_records.count()
    present_count = attendance_records.filter(status='present').count()
    absent_count = attendance_records.filter(status='absent').count()
    
    if total_classes > 0:
        attendance_percentage = round((present_count / total_classes) * 100, 2)
    else:
        attendance_percentage = 0
    
    # Filter by month and year
    form = StudentAttendanceFilterForm(request.GET)
    if form.is_valid():
        month = form.cleaned_data.get('month')
        year = form.cleaned_data.get('year')
        
        if month:
            attendance_records = attendance_records.filter(attendance__date__month=month)
        if year:
            attendance_records = attendance_records.filter(attendance__date__year=year)
    
    # Pagination
    paginator = Paginator(attendance_records, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'attendance_records': page_obj,
        'total_classes': total_classes,
        'present_count': present_count,
        'absent_count': absent_count,
        'attendance_percentage': attendance_percentage,
        'form': form,
        'page_obj': page_obj,
    }
    return render(request, 'attendance/my_attendance.html', context)

@login_required
@user_passes_test(is_teacher)
def bulk_attendance(request):
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST)
        if form.is_valid():
            class_info = form.cleaned_data['class_info']
            subject = form.cleaned_data['subject']
            attendance_date = form.cleaned_data['date']
            period = form.cleaned_data['period']
            default_status = form.cleaned_data['status']
            
            students = Student.objects.filter(class_info=class_info, is_active=True)
            
            # Check if attendance already exists
            existing_attendance = Attendance.objects.filter(
                class_info=class_info,
                subject=subject,
                date=attendance_date,
                period=period
            ).first()
            
            if existing_attendance:
                messages.warning(request, 'ইতিমধ্যেই উপস্থিতি নেওয়া হয়েছে')
                return redirect('attendance:attendance_detail', attendance_id=existing_attendance.id)
            
            # Create attendance record
            attendance = Attendance.objects.create(
                class_info=class_info,
                subject=subject,
                date=attendance_date,
                period=period,
                teacher=request.user
            )
            
            # Create attendance records for all students with default status
            for student in students:
                AttendanceRecord.objects.create(
                    attendance=attendance,
                    student=student,
                    status=default_status,
                    remarks='বাল্ক এন্ট্রি'
                )
            
            messages.success(request, f'{class_info} শ্রেণীর জন্য বাল্ক উপস্থিতি সফলভাবে সংরক্ষণ করা হয়েছে')
            return redirect('attendance:attendance_detail', attendance_id=attendance.id)
    else:
        form = BulkAttendanceForm()
    
    context = {
        'form': form,
    }
    return render(request, 'attendance/bulk_attendance.html', context)

@login_required
def attendance_report(request):
    if not hasattr(request.user, 'student'):
        messages.error(request, 'আপনি একজন শিক্ষার্থী নন')
        return redirect('dashboard')
    
    student = request.user.student
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # Get monthly reports
    monthly_reports = MonthlyReport.objects.filter(
        student=student,
        year=current_year
    ).order_by('month')
    
    # Get current month attendance
    current_month_attendance = AttendanceRecord.objects.filter(
        student=student,
        attendance__date__year=current_year,
        attendance__date__month=current_month
    )
    
    context = {
        'student': student,
        'monthly_reports': monthly_reports,
        'current_month_attendance': current_month_attendance,
        'current_year': current_year,
        'current_month': current_month,
    }
    return render(request, 'attendance/attendance_report.html', context)

@login_required
@user_passes_test(is_teacher)
def class_attendance_summary(request, class_id):
    class_info = get_object_or_404(Class, id=class_id)
    students = Student.objects.filter(class_info=class_info, is_active=True)
    
    # Get current month and year
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # Calculate attendance for each student
    student_attendance = []
    for student in students:
        monthly_attendance = AttendanceRecord.objects.filter(
            student=student,
            attendance__date__year=current_year,
            attendance__date__month=current_month
        )
        
        total_classes = monthly_attendance.count()
        present_count = monthly_attendance.filter(status='present').count()
        
        if total_classes > 0:
            attendance_percentage = round((present_count / total_classes) * 100, 2)
        else:
            attendance_percentage = 0
        
        student_attendance.append({
            'student': student,
            'total_classes': total_classes,
            'present_count': present_count,
            'attendance_percentage': attendance_percentage,
        })
    
    context = {
        'class_info': class_info,
        'student_attendance': student_attendance,
        'current_month': current_month,
        'current_year': current_year,
        'month_name': calendar.month_name[current_month],
    }
    return render(request, 'attendance/class_attendance_summary.html', context)

# API Views for AJAX calls
@login_required
def get_students_by_class(request):
    class_id = request.GET.get('class_id')
    if class_id:
        students = Student.objects.filter(class_info_id=class_id, is_active=True).order_by('roll_number')
        student_data = [{
            'id': student.id,
            'roll_number': student.roll_number,
            'name': student.name,
        } for student in students]
        return JsonResponse(student_data, safe=False)
    return JsonResponse([], safe=False)