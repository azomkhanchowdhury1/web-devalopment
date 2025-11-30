from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Avg, Count, Sum
from django.core.paginator import Paginator
import csv
import io

from .models import Result, Student, Class, Subject, GradeSystem
from .forms import ResultForm, BulkResultUploadForm, ResultFilterForm

def is_teacher(user):
    return user.groups.filter(name='Teachers').exists() or user.is_staff

def is_student(user):
    return user.groups.filter(name='Students').exists()

@login_required
def results_dashboard(request):
    # Check if user is teacher or admin
    if not (request.user.is_staff or is_teacher(request.user)):
        messages.error(request, "You don't have permission to access this page.")
        return redirect('my_results')
    
    form = ResultFilterForm(request.GET or None)
    results = Result.objects.all().select_related('student', 'subject', 'student_class')
    
    if form.is_valid():
        class_filter = form.cleaned_data.get('class_filter')
        exam_filter = form.cleaned_data.get('exam_filter')
        student_filter = form.cleaned_data.get('student_filter')
        
        if class_filter:
            results = results.filter(student_class=class_filter)
        if exam_filter:
            results = results.filter(exam_type=exam_filter)
        if student_filter:
            results = results.filter(student=student_filter)
    
    # Statistics
    total_results = results.count()
    average_percentage = results.aggregate(avg=Avg('percentage'))['avg'] or 0
    top_grade_count = results.filter(grade='A+').count()
    failed_count = results.filter(grade='F').count()
    
    # Pagination
    paginator = Paginator(results, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'results': page_obj,
        'form': form,
        'total_results': total_results,
        'average_percentage': round(average_percentage, 2),
        'top_grade_count': top_grade_count,
        'failed_count': failed_count,
        'classes': Class.objects.all(),
    }
    return render(request, 'result/results_dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or is_teacher(u))
def enter_result(request):
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.created_by = request.user
            result.save()
            messages.success(request, f'Result for {result.student.name} has been saved successfully!')
            return redirect('results_dashboard')
    else:
        form = ResultForm()
    
    context = {
        'form': form,
        'students': Student.objects.all().order_by('name'),
        'classes': Class.objects.all(),
        'subjects': Subject.objects.all(),
    }
    return render(request, 'result/enter_result.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or is_teacher(u))
def edit_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    
    if request.method == 'POST':
        form = ResultForm(request.POST, instance=result)
        if form.is_valid():
            form.save()
            messages.success(request, f'Result for {result.student.name} has been updated successfully!')
            return redirect('results_dashboard')
    else:
        form = ResultForm(instance=result)
    
    context = {
        'form': form,
        'result': result,
        'students': Student.objects.all().order_by('name'),
        'classes': Class.objects.all(),
        'subjects': Subject.objects.all(),
    }
    return render(request, 'result/edit_result.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or is_teacher(u))
def delete_result(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    if request.method == 'POST':
        student_name = result.student.name
        result.delete()
        messages.success(request, f'Result for {student_name} has been deleted successfully!')
        return redirect('results_dashboard')
    return render(request, 'result/confirm_delete.html', {'result': result})

@login_required
def my_results(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('home')
    
    results = Result.objects.filter(student=student).select_related('subject', 'student_class')
    
    # Calculate statistics
    total_subjects = results.values('subject').distinct().count()
    average_percentage = results.aggregate(avg=Avg('percentage'))['avg'] or 0
    
    # Calculate overall grade based on average percentage
    if average_percentage >= 80:
        overall_grade = 'A+'
    elif average_percentage >= 70:
        overall_grade = 'A'
    elif average_percentage >= 60:
        overall_grade = 'A-'
    elif average_percentage >= 50:
        overall_grade = 'B'
    elif average_percentage >= 40:
        overall_grade = 'C'
    elif average_percentage >= 33:
        overall_grade = 'D'
    else:
        overall_grade = 'F'
    
    # Get final results for report card
    final_results = results.filter(exam_type='final')
    
    # Calculate total GPA for final results
    if final_results.exists():
        total_gpa = final_results.aggregate(avg_gpa=Avg('gpa'))['avg_gpa'] or 0
    else:
        total_gpa = 0
    
    # Simple position calculation (this would need more complex logic in real scenario)
    position_in_class = "Not Available"  # This would require additional logic
    
    context = {
        'student': student,
        'results': results,
        'final_results': final_results,
        'total_subjects': total_subjects,
        'average_percentage': round(average_percentage, 2),
        'overall_grade': overall_grade,
        'position_in_class': position_in_class,
        'total_gpa': round(total_gpa, 2),
    }
    return render(request, 'result/my_results.html', context)

@login_required
def result_detail(request, result_id):
    result = get_object_or_404(Result, id=result_id)
    
    # Check if user has permission to view this result
    if not (request.user.is_staff or is_teacher(request.user) or 
            (is_student(request.user) and result.student.user == request.user)):
        messages.error(request, "You don't have permission to view this result.")
        return redirect('my_results')
    
    # Get performance history for this student in the same subject
    performance_history = Result.objects.filter(
        student=result.student, 
        subject=result.subject
    ).exclude(id=result_id).order_by('-created_at')[:10]
    
    context = {
        'result': result,
        'performance_history': performance_history,
        'school_name': 'Your School Name',  # This should come from settings
        'academic_year': '2024',  # This should be dynamic
    }
    return render(request, 'result/result_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or is_teacher(u))
def bulk_upload_results(request):
    if request.method == 'POST':
        form = BulkResultUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            class_choice = form.cleaned_data['class_choice']
            subject_choice = form.cleaned_data['subject_choice']
            exam_type = form.cleaned_data['exam_type']
            
            # Read CSV file
            try:
                data_set = csv_file.read().decode('UTF-8')
                io_string = io.StringIO(data_set)
                reader = csv.reader(io_string, delimiter=',')
                
                success_count = 0
                error_count = 0
                errors = []
                
                # Skip header
                next(reader, None)
                
                for row_num, row in enumerate(reader, 2):  # Start from line 2 for error reporting
                    if len(row) >= 2:
                        try:
                            roll_number = row[0].strip()
                            marks_obtained = float(row[1])
                            
                            # Find student
                            try:
                                student = Student.objects.get(
                                    roll_number=roll_number, 
                                    current_class=class_choice
                                )
                            except Student.DoesNotExist:
                                errors.append(f"Line {row_num}: Student with roll number {roll_number} not found in selected class")
                                error_count += 1
                                continue
                            
                            # Check if result already exists
                            if Result.objects.filter(
                                student=student, 
                                subject=subject_choice, 
                                exam_type=exam_type
                            ).exists():
                                errors.append(f"Line {row_num}: Result already exists for {student.name}")
                                error_count += 1
                                continue
                            
                            # Create result
                            Result.objects.create(
                                student=student,
                                student_class=class_choice,
                                subject=subject_choice,
                                exam_type=exam_type,
                                marks_obtained=marks_obtained,
                                total_marks=100,  # Default total marks
                                created_by=request.user
                            )
                            success_count += 1
                            
                        except ValueError:
                            errors.append(f"Line {row_num}: Invalid marks format")
                            error_count += 1
                        except Exception as e:
                            errors.append(f"Line {row_num}: {str(e)}")
                            error_count += 1
                
                if success_count > 0:
                    messages.success(request, f'Successfully uploaded {success_count} results!')
                if error_count > 0:
                    messages.warning(request, f'{error_count} results could not be uploaded.')
                    for error in errors[:10]:  # Show first 10 errors
                        messages.error(request, error)
                
                return redirect('results_dashboard')
                
            except Exception as e:
                messages.error(request, f'Error processing CSV file: {str(e)}')
    else:
        form = BulkResultUploadForm()
    
    context = {
        'form': form,
    }
    return render(request, 'result/bulk_upload.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff or is_teacher(u))
def download_result_template(request):
    # Create a CSV template file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="result_template.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['roll_number', 'marks_obtained'])
    writer.writerow(['2024001', '85'])
    writer.writerow(['2024002', '92'])
    writer.writerow(['2024003', '78'])
    
    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def manage_grade_system(request):
    grades = GradeSystem.objects.all().order_by('min_percentage')
    
    if request.method == 'POST':
        # Handle grade system updates
        pass
    
    context = {
        'grades': grades,
    }
    return render(request, 'result/grade_system.html', context)

# API views for AJAX calls
@login_required
def get_students_by_class(request):
    class_id = request.GET.get('class_id')
    if class_id:
        students = Student.objects.filter(current_class_id=class_id).order_by('roll_number')
        data = [{'id': s.id, 'name': f'{s.name} - {s.roll_number}'} for s in students]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)

@login_required
def get_subjects_by_class(request):
    class_id = request.GET.get('class_id')
    if class_id:
        subjects = Subject.objects.filter(class_associated_id=class_id).order_by('name')
        data = [{'id': s.id, 'name': s.name} for s in subjects]
        return JsonResponse(data, safe=False)
    return JsonResponse([], safe=False)