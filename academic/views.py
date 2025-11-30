from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import AcademicYear, Subject, Class, ClassRoutine
from .forms import AcademicYearForm, SubjectForm, ClassForm, ClassRoutineForm

def is_teacher_or_admin(user):
    return user.groups.filter(name__in=['Teachers', 'Admins']).exists() or user.is_superuser

@login_required
def academic_year_list(request):
    academic_years = AcademicYear.objects.all()
    return render(request, 'academic/academic_year_list.html', {
        'academic_years': academic_years
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Admins').exists())
def academic_year_create(request):
    if request.method == 'POST':
        form = AcademicYearForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic year created successfully!')
            return redirect('academic_year_list')
    else:
        form = AcademicYearForm()
    
    return render(request, 'academic/academic_year_form.html', {
        'form': form,
        'title': 'Add Academic Year'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Admins').exists())
def academic_year_edit(request, pk):
    academic_year = get_object_or_404(AcademicYear, pk=pk)
    
    if request.method == 'POST':
        form = AcademicYearForm(request.POST, instance=academic_year)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic year updated successfully!')
            return redirect('academic_year_list')
    else:
        form = AcademicYearForm(instance=academic_year)
    
    return render(request, 'academic/academic_year_form.html', {
        'form': form,
        'title': 'Edit Academic Year'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Admins').exists())
def academic_year_delete(request, pk):
    academic_year = get_object_or_404(AcademicYear, pk=pk)
    
    if request.method == 'POST':
        academic_year.delete()
        messages.success(request, 'Academic year deleted successfully!')
        return redirect('academic_year_list')
    
    return render(request, 'academic/academic_year_confirm_delete.html', {
        'academic_year': academic_year
    })

@login_required
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'academic/subject_list.html', {
        'subjects': subjects
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def subject_create(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject created successfully!')
            return redirect('subject_list')
    else:
        form = SubjectForm()
    
    return render(request, 'academic/subject_form.html', {
        'form': form,
        'title': 'Add Subject'
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('subject_list')
    else:
        form = SubjectForm(instance=subject)
    
    return render(request, 'academic/subject_form.html', {
        'form': form,
        'title': 'Edit Subject'
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    
    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')
        return redirect('subject_list')
    
    return render(request, 'academic/subject_confirm_delete.html', {
        'subject': subject
    })

@login_required
def class_list(request):
    classes = Class.objects.select_related('class_teacher', 'academic_year').prefetch_related('subjects')
    return render(request, 'academic/class_list.html', {
        'classes': classes
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def class_create(request):
    if request.method == 'POST':
        form = ClassForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class created successfully!')
            return redirect('class_list')
    else:
        form = ClassForm()
    
    return render(request, 'academic/class_form.html', {
        'form': form,
        'title': 'Add Class'
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def class_edit(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('class_list')
    else:
        form = ClassForm(instance=class_obj)
    
    return render(request, 'academic/class_form.html', {
        'form': form,
        'title': 'Edit Class'
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def class_delete(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    
    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, 'Class deleted successfully!')
        return redirect('class_list')
    
    return render(request, 'academic/class_confirm_delete.html', {
        'class_obj': class_obj
    })

@login_required
def class_detail(request, pk):
    class_obj = get_object_or_404(Class, pk=pk)
    routines = ClassRoutine.objects.filter(class_obj=class_obj, is_active=True)
    students = class_obj.student_set.all()
    
    return render(request, 'academic/class_detail.html', {
        'class_obj': class_obj,
        'routines': routines,
        'students': students
    })

@login_required
def routine_list(request):
    class_filter = request.GET.get('class')
    
    routines = ClassRoutine.objects.select_related(
        'class_obj', 'subject', 'teacher'
    ).filter(is_active=True)
    
    if class_filter:
        routines = routines.filter(class_obj_id=class_filter)
    
    classes = Class.objects.filter(is_active=True)
    
    return render(request, 'academic/routine_list.html', {
        'routines': routines,
        'classes': classes
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def routine_create(request):
    if request.method == 'POST':
        form = ClassRoutineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class routine created successfully!')
            return redirect('routine_list')
    else:
        form = ClassRoutineForm()
    
    return render(request, 'academic/routine_form.html', {
        'form': form,
        'title': 'Add Class Routine'
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def routine_edit(request, pk):
    routine = get_object_or_404(ClassRoutine, pk=pk)
    
    if request.method == 'POST':
        form = ClassRoutineForm(request.POST, instance=routine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Class routine updated successfully!')
            return redirect('routine_list')
    else:
        form = ClassRoutineForm(instance=routine)
    
    return render(request, 'academic/routine_form.html', {
        'form': form,
        'title': 'Edit Class Routine'
    })

@login_required
@user_passes_test(is_teacher_or_admin)
def routine_delete(request, pk):
    routine = get_object_or_404(ClassRoutine, pk=pk)
    
    if request.method == 'POST':
        routine.delete()
        messages.success(request, 'Class routine deleted successfully!')
        return redirect('routine_list')
    
    return render(request, 'academic/routine_confirm_delete.html', {
        'routine': routine
    })

@login_required
def get_class_routine(request, class_id):
    routines = ClassRoutine.objects.filter(
        class_obj_id=class_id, 
        is_active=True
    ).select_related('subject', 'teacher').order_by('day', 'period')
    
    routine_data = {}
    for routine in routines:
        if routine.day not in routine_data:
            routine_data[routine.day] = []
        
        routine_data[routine.day].append({
            'period': routine.period,
            'subject': routine.subject.name,
            'teacher': routine.teacher.get_full_name(),
            'start_time': routine.start_time.strftime('%H:%M'),
            'end_time': routine.end_time.strftime('%H:%M'),
            'room': routine.room
        })
    
    return JsonResponse(routine_data)