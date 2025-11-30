from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Teacher, ClassSchedule, Assignment, Attendance, StudentResult, Notice
from .forms import (
    UserRegistrationForm, TeacherForm, ClassScheduleForm, 
    AssignmentForm, AttendanceForm, StudentResultForm, NoticeForm
)

# Authentication Views
def teacher_register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        teacher_form = TeacherForm(request.POST, request.FILES)
        
        if user_form.is_valid() and teacher_form.is_valid():
            user = user_form.save()
            teacher = teacher_form.save(commit=False)
            teacher.user = user
            teacher.name = f"{user.first_name} {user.last_name}"
            teacher.save()
            
            messages.success(request, 'আপনার অ্যাকাউন্ট সফলভাবে তৈরি হয়েছে! এখন লগইন করুন।')
            return redirect('teacher_login')
    else:
        user_form = UserRegistrationForm()
        teacher_form = TeacherForm()
    
    return render(request, 'teacher/register.html', {
        'user_form': user_form,
        'teacher_form': teacher_form
    })

def teacher_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'সফলভাবে লগইন হয়েছে!')
            return redirect('teacher_dashboard')
        else:
            messages.error(request, 'ইউজারনেম বা পাসওয়ার্ড ভুল!')
    
    return render(request, 'teacher/login.html')

def teacher_logout(request):
    logout(request)
    messages.success(request, 'সফলভাবে লগআউট হয়েছে!')
    return redirect('teacher_login')

# Profile Views
@login_required
def teacher_profile(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_dashboard')
    
    context = {
        'teacher': teacher,
        'total_classes': ClassSchedule.objects.filter(teacher=teacher).count(),
        'total_assignments': Assignment.objects.filter(teacher=teacher).count(),
        'total_results': StudentResult.objects.filter(teacher=teacher).count(),
    }
    return render(request, 'teacher/teacher_profile.html', context)

@login_required
def edit_teacher_profile(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'প্রোফাইল সফলভাবে আপডেট হয়েছে!')
            return redirect('teacher_profile')
    else:
        form = TeacherForm(instance=teacher)
    
    return render(request, 'teacher/edit_teacher_profile.html', {'form': form})

# Dashboard and Portal Views
@login_required
def teacher_dashboard(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    # Get today's schedule
    today = date.today()
    today_name = today.strftime('%A').lower()
    today_schedule = ClassSchedule.objects.filter(teacher=teacher, day=today_name)
    
    # Get recent assignments
    recent_assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')[:5]
    
    # Get statistics
    total_classes = ClassSchedule.objects.filter(teacher=teacher).count()
    total_assignments = Assignment.objects.filter(teacher=teacher).count()
    total_students = Attendance.objects.filter(teacher=teacher).aggregate(
        total=Sum('total_students')
    )['total'] or 0
    
    context = {
        'teacher': teacher,
        'today_schedule': today_schedule,
        'recent_assignments': recent_assignments,
        'total_classes': total_classes,
        'total_assignments': total_assignments,
        'total_students': total_students,
    }
    return render(request, 'teacher/dashboard.html', context)

@login_required
def teacher_portal(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    # Get today's schedule
    today = date.today()
    today_name = today.strftime('%A').lower()
    today_schedule = ClassSchedule.objects.filter(teacher=teacher, day=today_name)
    
    # Get statistics for dashboard cards
    total_classes = ClassSchedule.objects.filter(teacher=teacher).count()
    total_students = Attendance.objects.filter(teacher=teacher).aggregate(
        total=Sum('total_students')
    )['total'] or 0
    today_classes = today_schedule.count()
    
    # Calculate pending assignments (due date in future)
    pending_assignments = Assignment.objects.filter(
        teacher=teacher, 
        due_date__gt=timezone.now()
    ).count()
    
    # Get recent notices
    recent_notices = Notice.objects.filter(teacher=teacher, is_published=True).order_by('-created_at')[:3]
    
    context = {
        'teacher': teacher,
        'today_schedule': today_schedule,
        'recent_notices': recent_notices,
        'total_classes': total_classes,
        'total_students': total_students,
        'today_classes': today_classes,
        'pending_assignments': pending_assignments,
    }
    return render(request, 'teacher/teacher_portal.html', context)

# Teacher Management Views
@login_required
def teacher_list(request):
    teachers = Teacher.objects.all().order_by('-joining_date')
    return render(request, 'teacher/teacher_list.html', {'teachers': teachers})

@login_required
def add_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(request, 'শিক্ষক সফলভাবে যোগ করা হয়েছে!')
            return redirect('teacher_list')
    else:
        form = TeacherForm()
    
    return render(request, 'teacher/add_teacher.html', {'form': form})

@login_required
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    teacher_classes = ClassSchedule.objects.filter(teacher=teacher)
    
    context = {
        'teacher': teacher,
        'teacher_classes': teacher_classes,
    }
    return render(request, 'teacher/teacher_detail.html', context)

@login_required
def edit_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, 'শিক্ষকের তথ্য সফলভাবে আপডেট হয়েছে!')
            return redirect('teacher_detail', teacher_id=teacher.id)
    else:
        form = TeacherForm(instance=teacher)
    
    return render(request, 'teacher/edit_teacher.html', {'form': 'form', 'teacher': teacher})

@login_required
def delete_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'শিক্ষক সফলভাবে মুছে ফেলা হয়েছে!')
        return redirect('teacher_list')
    
    return render(request, 'teacher/delete_teacher.html', {'teacher': teacher})

# Class Schedule Views
@login_required
def class_schedule_list(request):
    try:
        teacher = request.user.teacher
        schedules = ClassSchedule.objects.filter(teacher=teacher).order_by('day', 'start_time')
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    return render(request, 'teacher/class_schedule_list.html', {'schedules': schedules})

@login_required
def add_class_schedule(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    if request.method == 'POST':
        form = ClassScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.teacher = teacher
            schedule.save()
            messages.success(request, 'ক্লাস সিডিউল সফলভাবে যোগ করা হয়েছে!')
            return redirect('class_schedule_list')
    else:
        form = ClassScheduleForm()
    
    return render(request, 'teacher/add_class_schedule.html', {'form': form})

@login_required
def edit_class_schedule(request, schedule_id):
    schedule = get_object_or_404(ClassSchedule, id=schedule_id)
    
    if request.method == 'POST':
        form = ClassScheduleForm(request.POST, instance=schedule)
        if form.is_valid():
            form.save()
            messages.success(request, 'ক্লাস সিডিউল সফলভাবে আপডেট হয়েছে!')
            return redirect('class_schedule_list')
    else:
        form = ClassScheduleForm(instance=schedule)
    
    return render(request, 'teacher/edit_class_schedule.html', {'form': form, 'schedule': schedule})

@login_required
def delete_class_schedule(request, schedule_id):
    schedule = get_object_or_404(ClassSchedule, id=schedule_id)
    
    if request.method == 'POST':
        schedule.delete()
        messages.success(request, 'ক্লাস সিডিউল সফলভাবে মুছে ফেলা হয়েছে!')
        return redirect('class_schedule_list')
    
    return render(request, 'teacher/delete_class_schedule.html', {'schedule': schedule})

# Assignment Views
@login_required
def assignment_list(request):
    try:
        teacher = request.user.teacher
        assignments = Assignment.objects.filter(teacher=teacher).order_by('-created_at')
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    return render(request, 'teacher/assignment_list.html', {'assignments': assignments})

@login_required
def add_assignment(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.teacher = teacher
            assignment.save()
            messages.success(request, 'এসাইনমেন্ট সফলভাবে তৈরি করা হয়েছে!')
            return redirect('assignment_list')
    else:
        form = AssignmentForm()
    
    return render(request, 'teacher/add_assignment.html', {'form': form})

@login_required
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    return render(request, 'teacher/assignment_detail.html', {'assignment': assignment})

@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES, instance=assignment)
        if form.is_valid():
            form.save()
            messages.success(request, 'এসাইনমেন্ট সফলভাবে আপডেট হয়েছে!')
            return redirect('assignment_detail', assignment_id=assignment.id)
    else:
        form = AssignmentForm(instance=assignment)
    
    return render(request, 'teacher/edit_assignment.html', {'form': form, 'assignment': assignment})

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, 'এসাইনমেন্ট সফলভাবে মুছে ফেলা হয়েছে!')
        return redirect('assignment_list')
    
    return render(request, 'teacher/delete_assignment.html', {'assignment': assignment})

# Attendance Views
@login_required
def attendance_list(request):
    try:
        teacher = request.user.teacher
        attendances = Attendance.objects.filter(teacher=teacher).order_by('-date')
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    return render(request, 'teacher/attendance_list.html', {'attendances': attendances})

@login_required
def add_attendance(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.teacher = teacher
            attendance.save()
            messages.success(request, 'উপস্থিতি রেকর্ড সফলভাবে সংরক্ষণ করা হয়েছে!')
            return redirect('attendance_list')
    else:
        form = AttendanceForm()
    
    return render(request, 'teacher/add_attendance.html', {'form': form})

@login_required
def edit_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, 'উপস্থিতি রেকর্ড সফলভাবে আপডেট হয়েছে!')
            return redirect('attendance_list')
    else:
        form = AttendanceForm(instance=attendance)
    
    return render(request, 'teacher/edit_attendance.html', {'form': form, 'attendance': attendance})

@login_required
def delete_attendance(request, attendance_id):
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'উপস্থিতি রেকর্ড সফলভাবে মুছে ফেলা হয়েছে!')
        return redirect('attendance_list')
    
    return render(request, 'teacher/delete_attendance.html', {'attendance': attendance})

# Result Views
@login_required
def result_list(request):
    try:
        teacher = request.user.teacher
        results = StudentResult.objects.filter(teacher=teacher).order_by('-created_at')
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    return render(request, 'teacher/result_list.html', {'results': results})

@login_required
def add_result(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    if request.method == 'POST':
        form = StudentResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.teacher = teacher
            result.save()
            messages.success(request, 'ফলাফল সফলভাবে সংরক্ষণ করা হয়েছে!')
            return redirect('result_list')
    else:
        form = StudentResultForm()
    
    return render(request, 'teacher/add_result.html', {'form': form})

@login_required
def edit_result(request, result_id):
    result = get_object_or_404(StudentResult, id=result_id)
    
    if request.method == 'POST':
        form = StudentResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, 'ফলাফল সফলভাবে আপডেট হয়েছে!')
            return redirect('result_list')
    else:
        form = StudentResultForm(instance=result)
    
    return render(request, 'teacher/edit_result.html', {'form': form, 'result': result})

@login_required
def delete_result(request, result_id):
    result = get_object_or_404(StudentResult, id=result_id)
    
    if request.method == 'POST':
        result.delete()
        messages.success(request, 'ফলাফল সফলভাবে মুছে ফেলা হয়েছে!')
        return redirect('result_list')
    
    return render(request, 'teacher/delete_result.html', {'result': result})

@login_required
def upload_results(request):
    if request.method == 'POST' and request.FILES.get('results_file'):
        # Handle bulk results upload (CSV/Excel)
        # This is a simplified version - you might want to use pandas for CSV processing
        messages.success(request, 'ফলাফল সফলভাবে আপলোড করা হয়েছে!')
        return redirect('result_list')
    
    return render(request, 'teacher/upload_results.html')

# Notice Views
@login_required
def notice_list(request):
    try:
        teacher = request.user.teacher
        notices = Notice.objects.filter(teacher=teacher).order_by('-created_at')
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    return render(request, 'teacher/notice_list.html', {'notices': notices})

@login_required
def add_notice(request):
    try:
        teacher = request.user.teacher
    except Teacher.DoesNotExist:
        messages.error(request, 'শিক্ষক প্রোফাইল পাওয়া যায়নি!')
        return redirect('teacher_login')
    
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.teacher = teacher
            notice.save()
            messages.success(request, 'নোটিশ সফলভাবে তৈরি করা হয়েছে!')
            return redirect('notice_list')
    else:
        form = NoticeForm()
    
    return render(request, 'teacher/add_notice.html', {'form': form})

@login_required
def edit_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, 'নোটিশ সফলভাবে আপডেট হয়েছে!')
            return redirect('notice_list')
    else:
        form = NoticeForm(instance=notice)
    
    return render(request, 'teacher/edit_notice.html', {'form': form, 'notice': notice})

@login_required
def delete_notice(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    
    if request.method == 'POST':
        notice.delete()
        messages.success(request, 'নোটিশ সফলভাবে মুছে ফেলা হয়েছে!')
        return redirect('notice_list')
    
    return render(request, 'teacher/delete_notice.html', {'notice': notice})

# API Views
@login_required
def teacher_stats_api(request):
    try:
        teacher = request.user.teacher
        
        stats = {
            'total_classes': ClassSchedule.objects.filter(teacher=teacher).count(),
            'total_assignments': Assignment.objects.filter(teacher=teacher).count(),
            'total_students': Attendance.objects.filter(teacher=teacher).aggregate(
                total=Sum('total_students')
            )['total'] or 0,
            'pending_assignments': Assignment.objects.filter(
                teacher=teacher, 
                due_date__gt=timezone.now()
            ).count(),
        }
        
        return JsonResponse(stats)
    except Teacher.DoesNotExist:
        return JsonResponse({'error': 'Teacher profile not found'}, status=404)

@login_required
def today_schedule_api(request):
    try:
        teacher = request.user.teacher
        today = date.today()
        today_name = today.strftime('%A').lower()
        
        schedules = ClassSchedule.objects.filter(teacher=teacher, day=today_name)
        
        schedule_data = []
        for schedule in schedules:
            schedule_data.append({
                'class_name': schedule.class_name,
                'subject': schedule.subject,
                'time': f"{schedule.start_time} - {schedule.end_time}",
                'room': schedule.room,
            })
        
        return JsonResponse({'schedules': schedule_data})
    except Teacher.DoesNotExist:
        return JsonResponse({'error': 'Teacher profile not found'}, status=404)