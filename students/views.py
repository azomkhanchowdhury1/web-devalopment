from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.utils import timezone
import pandas as pd
import json
from datetime import datetime

from .models import Student, Guardian, Fee, Document, AcademicHistory, Grade, Attendance
from .forms import (
    StudentForm, GuardianForm, FeeForm, DocumentForm, AcademicHistoryForm,
    BulkUploadForm, PromoteStudentsForm
)


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Student.objects.select_related('grade', 'guardian')
        
        # Filter by grade if provided
        grade = self.request.GET.get('grade')
        if grade:
            queryset = queryset.filter(grade__name=grade)
        
        # Filter by status if provided
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(roll_number__icontains=search_query) |
                Q(phone__icontains=search_query)
            )
        
        return queryset.order_by('grade__name', 'roll_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grades'] = Grade.objects.all()
        context['status_choices'] = Student.STATUS_CHOICES
        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = Document.objects.filter(student=self.object)
        context['academic_history'] = AcademicHistory.objects.filter(student=self.object)
        context['fee_history'] = Fee.objects.filter(student=self.object)
        return context


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'শিক্ষার্থী সফলভাবে যোগ করা হয়েছে')
        return super().form_valid(form)


class StudentUpdateView(LoginRequiredMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_edit.html'
    
    def get_success_url(self):
        return reverse_lazy('students:student_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'শিক্ষার্থীর তথ্য সফলভাবে আপডেট করা হয়েছে')
        return super().form_valid(form)


class StudentDeleteView(LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('students:student_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'শিক্ষার্থী সফলভাবে মুছে ফেলা হয়েছে')
        return super().delete(request, *args, **kwargs)


class GuardianUpdateView(LoginRequiredMixin, UpdateView):
    model = Guardian
    form_class = GuardianForm
    template_name = 'students/guardian_edit.html'
    
    def get_object(self):
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        guardian, created = Guardian.objects.get_or_create(
            pk=student.guardian.pk if student.guardian else None
        )
        return guardian
    
    def get_success_url(self):
        return reverse_lazy('students:student_detail', kwargs={'pk': self.kwargs['student_id']})
    
    def form_valid(self, form):
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        guardian = form.save()
        student.guardian = guardian
        student.save()
        messages.success(self.request, 'অভিভাবকের তথ্য সফলভাবে আপডেট করা হয়েছে')
        return super().form_valid(form)


class FeeListView(LoginRequiredMixin, ListView):
    model = Fee
    template_name = 'students/fee_list.html'
    context_object_name = 'fees'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = Fee.objects.select_related('student')
        
        # Filter by month and year
        month = self.request.GET.get('month')
        year = self.request.GET.get('year')
        status = self.request.GET.get('status')
        
        if month:
            queryset = queryset.filter(month=month)
        if year:
            queryset = queryset.filter(year=year)
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-year', '-month', 'student__roll_number')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['months'] = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        context['current_year'] = timezone.now().year
        return context


class FeeCreateView(LoginRequiredMixin, CreateView):
    model = Fee
    form_class = FeeForm
    template_name = 'students/fee_add.html'
    success_url = reverse_lazy('students:fee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ফি সফলভাবে যোগ করা হয়েছে')
        return super().form_valid(form)


class FeeUpdateView(LoginRequiredMixin, UpdateView):
    model = Fee
    form_class = FeeForm
    template_name = 'students/fee_edit.html'
    success_url = reverse_lazy('students:fee_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'ফি তথ্য সফলভাবে আপডেট করা হয়েছে')
        return super().form_valid(form)


class FeeDeleteView(LoginRequiredMixin, DeleteView):
    model = Fee
    template_name = 'students/fee_confirm_delete.html'
    success_url = reverse_lazy('students:fee_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'ফি রেকর্ড সফলভাবে মুছে ফেলা হয়েছে')
        return super().delete(request, *args, **kwargs)


class DocumentCreateView(LoginRequiredMixin, CreateView):
    model = Document
    form_class = DocumentForm
    template_name = 'students/document_add.html'
    
    def get_success_url(self):
        return reverse_lazy('students:student_detail', kwargs={'pk': self.kwargs['student_id']})
    
    def form_valid(self, form):
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        form.instance.student = student
        messages.success(self.request, 'নথি সফলভাবে আপলোড করা হয়েছে')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = get_object_or_404(Student, pk=self.kwargs['student_id'])
        return context


class DocumentDeleteView(LoginRequiredMixin, DeleteView):
    model = Document
    template_name = 'students/document_confirm_delete.html'
    
    def get_success_url(self):
        return reverse_lazy('students:student_detail', kwargs={'pk': self.object.student.pk})
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'নথি সফলভাবে মুছে ফেলা হয়েছে')
        return super().delete(request, *args, **kwargs)


class AcademicHistoryCreateView(LoginRequiredMixin, CreateView):
    model = AcademicHistory
    form_class = AcademicHistoryForm
    template_name = 'students/academic_history_add.html'
    
    def get_success_url(self):
        return reverse_lazy('students:student_detail', kwargs={'pk': self.kwargs['student_id']})
    
    def form_valid(self, form):
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        form.instance.student = student
        messages.success(self.request, 'একাডেমিক ইতিহাস সফলভাবে যোগ করা হয়েছে')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['student'] = get_object_or_404(Student, pk=self.kwargs['student_id'])
        return context


class BulkUploadView(LoginRequiredMixin, TemplateView):
    template_name = 'students/bulk_upload.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = BulkUploadForm()
        return context
    
    def post(self, request, *args, **kwargs):
        form = BulkUploadForm(request.POST, request.FILES)
        context = self.get_context_data()
        
        if form.is_valid():
            file = request.FILES['file']
            try:
                # Read the uploaded file
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                success_count = 0
                errors = []
                
                for index, row in df.iterrows():
                    try:
                        # Validate required fields
                        required_fields = ['first_name', 'last_name', 'roll_number', 'grade']
                        for field in required_fields:
                            if field not in df.columns or pd.isna(row[field]):
                                errors.append({
                                    'row': index + 2,  # +2 because of header and 0-based index
                                    'message': f'{field} ফিল্ডটি প্রয়োজনীয়'
                                })
                                continue
                        
                        # Check if student already exists
                        if Student.objects.filter(roll_number=row['roll_number']).exists():
                            errors.append({
                                'row': index + 2,
                                'message': f'রোল নম্বর {row["roll_number"]} ইতিমধ্যে存在'
                            })
                            continue
                        
                        # Get or create grade
                        grade_name = row['grade']
                        section = row.get('section')
                        grade, created = Grade.objects.get_or_create(
                            name=grade_name,
                            section=section if section and not pd.isna(section) else None
                        )
                        
                        # Create student
                        student = Student(
                            first_name=row['first_name'],
                            last_name=row['last_name'],
                            roll_number=row['roll_number'],
                            grade=grade,
                            created_by=request.user
                        )
                        
                        # Optional fields
                        if 'date_of_birth' in df.columns and not pd.isna(row['date_of_birth']):
                            student.date_of_birth = row['date_of_birth']
                        if 'gender' in df.columns and not pd.isna(row['gender']):
                            student.gender = row['gender']
                        if 'phone' in df.columns and not pd.isna(row['phone']):
                            student.phone = row['phone']
                        if 'email' in df.columns and not pd.isna(row['email']):
                            student.email = row['email']
                        if 'address' in df.columns and not pd.isna(row['address']):
                            student.address = row['address']
                        
                        student.save()
                        success_count += 1
                        
                    except Exception as e:
                        errors.append({
                            'row': index + 2,
                            'message': f'ত্রুটি: {str(e)}'
                        })
                
                context['upload_result'] = {
                    'success_count': success_count,
                    'errors': errors
                }
                messages.success(request, f'{success_count} জন শিক্ষার্থী সফলভাবে যোগ করা হয়েছে')
                
            except Exception as e:
                messages.error(request, f'ফাইল প্রসেস করতে সমস্যা: {str(e)}')
        
        else:
            messages.error(request, 'অবৈধ ফাইল ফরম্যাট')
        
        return self.render_to_response(context)


class PromoteStudentsView(LoginRequiredMixin, TemplateView):
    template_name = 'students/promote_student.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PromoteStudentsForm()
        context['grades'] = Grade.objects.values_list('name', flat=True).distinct()
        context['sections'] = Grade.objects.exclude(section__isnull=True).values_list('section', flat=True).distinct()
        
        # Get students for current selection
        current_grade = self.request.GET.get('current_grade')
        current_section = self.request.GET.get('current_section')
        
        if current_grade:
            students = Student.objects.filter(grade__name=current_grade, status='Active')
            if current_section:
                students = students.filter(grade__section=current_section)
            context['students'] = students
        
        return context
    
    def post(self, request, *args, **kwargs):
        form = PromoteStudentsForm(request.POST)
        context = self.get_context_data()
        
        if form.is_valid():
            current_grade = form.cleaned_data['current_grade']
            current_section = form.cleaned_data['current_section']
            next_grade = form.cleaned_data['next_grade']
            next_section = form.cleaned_data['next_section']
            academic_year = form.cleaned_data['academic_year']
            update_roll_numbers = form.cleaned_data['update_roll_numbers']
            
            # Get students to promote
            students = Student.objects.filter(grade__name=current_grade, status='Active')
            if current_section:
                students = students.filter(grade__section=current_section)
            
            promoted_count = 0
            
            for student in students:
                # Create academic history record
                AcademicHistory.objects.create(
                    student=student,
                    academic_year=academic_year,
                    grade=current_grade,
                    section=current_section,
                    roll_number=student.roll_number,
                    status='Promoted',
                    remarks=f'প্রমোশন করা হয়েছে {next_grade} এ'
                )
                
                # Update student's current grade
                next_grade_obj, created = Grade.objects.get_or_create(
                    name=next_grade,
                    section=next_section if next_section else None
                )
                student.grade = next_grade_obj
                
                # Update roll number if requested
                if update_roll_numbers:
                    # Simple roll number update logic - you might want to customize this
                    student.roll_number = f"{next_grade}{student.pk:03d}"
                
                student.save()
                promoted_count += 1
            
            messages.success(request, f'{promoted_count} জন শিক্ষার্থী সফলভাবে প্রমোশন করা হয়েছে')
            return redirect('students:student_list')
        
        context['form'] = form
        return self.render_to_response(context)


class StudentPortalView(LoginRequiredMixin, TemplateView):
    template_name = 'students/student_portal.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # For demonstration, get the first student
        # In real application, you might want to get the logged-in student
        student = Student.objects.first()
        
        if student:
            context['student'] = student
            context['current_academic_year'] = f"{timezone.now().year}-{timezone.now().year + 1}"
            
            # Attendance summary for current month
            current_month = timezone.now().month
            current_year = timezone.now().year
            
            attendance_data = Attendance.objects.filter(
                student=student,
                date__month=current_month,
                date__year=current_year
            )
            
            context['attendance_summary'] = {
                'present': attendance_data.filter(status='Present').count(),
                'absent': attendance_data.filter(status='Absent').count(),
                'late': attendance_data.filter(status='Late').count(),
                'total': attendance_data.count(),
                'percentage': (attendance_data.filter(status='Present').count() / attendance_data.count() * 100) if attendance_data.count() > 0 else 0
            }
            
            # Recent results (mock data)
            context['recent_results'] = []
            
            # Fee details
            context['fee_details'] = Fee.objects.filter(student=student).order_by('-year', '-month')[:6]
            
            # Documents
            context['documents'] = Document.objects.filter(student=student).order_by('-uploaded_at')[:10]
        
        return context


class StudentStatisticsView(LoginRequiredMixin, TemplateView):
    template_name = 'students/student_statistics.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Basic counts
        context['total_students'] = Student.objects.count()
        context['active_students'] = Student.objects.filter(status='Active').count()
        context['male_students'] = Student.objects.filter(gender='Male').count()
        context['female_students'] = Student.objects.filter(gender='Female').count()
        
        # Grade-wise statistics
        grade_stats = Student.objects.values('grade__name').annotate(
            count=Count('id')
        ).order_by('grade__name')
        
        total_students = context['total_students']
        for stat in grade_stats:
            stat['percentage'] = (stat['count'] / total_students * 100) if total_students > 0 else 0
        
        context['grade_stats'] = grade_stats
        
        # Section-wise statistics
        section_stats = Student.objects.exclude(grade__section__isnull=True).values(
            'grade__section'
        ).annotate(
            count=Count('id')
        ).order_by('grade__section')
        
        for stat in section_stats:
            stat['percentage'] = (stat['count'] / total_students * 100) if total_students > 0 else 0
        
        context['section_stats'] = section_stats
        
        # Blood group statistics
        blood_group_stats = Student.objects.exclude(blood_group__isnull=True).values(
            'blood_group'
        ).annotate(
            count=Count('id')
        ).order_by('blood_group')
        
        for stat in blood_group_stats:
            stat['percentage'] = (stat['count'] / total_students * 100) if total_students > 0 else 0
        
        context['blood_group_stats'] = blood_group_stats
        
        # Status statistics
        status_stats = Student.objects.values('status').annotate(
            count=Count('id')
        ).order_by('status')
        
        for stat in status_stats:
            stat['percentage'] = (stat['count'] / total_students * 100) if total_students > 0 else 0
        
        context['status_stats'] = status_stats
        
        # Monthly admission statistics (current year)
        current_year = timezone.now().year
        monthly_data = []
        
        for month in range(1, 13):
            count = Student.objects.filter(
                admission_date__year=current_year,
                admission_date__month=month
            ).count()
            
            monthly_data.append({
                'month': datetime(current_year, month, 1).strftime('%B'),
                'count': count,
                'growth': 0,  # You can calculate growth from previous year
                'percentage': (count / context['total_students'] * 100) if context['total_students'] > 0 else 0
            })
        
        context['monthly_admissions'] = monthly_data
        context['current_year'] = current_year
        
        return context


# API Views for AJAX calls
def get_students_by_grade(request):
    grade_name = request.GET.get('grade')
    section = request.GET.get('section')
    
    students = Student.objects.filter(grade__name=grade_name, status='Active')
    if section:
        students = students.filter(grade__section=section)
    
    student_list = list(students.values('id', 'first_name', 'last_name', 'roll_number'))
    return JsonResponse(student_list, safe=False)


def get_student_counts(request):
    total = Student.objects.count()
    active = Student.objects.filter(status='Active').count()
    male = Student.objects.filter(gender='Male').count()
    female = Student.objects.filter(gender='Female').count()
    
    return JsonResponse({
        'total': total,
        'active': active,
        'male': male,
        'female': female
    })