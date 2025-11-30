from django import forms
from django.core.exceptions import ValidationError
from .models import Student, Guardian, Fee, Document, AcademicHistory, Grade, Attendance
from django.utils import timezone
import datetime


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'roll_number', 'date_of_birth', 'gender',
            'blood_group', 'photo', 'grade', 'admission_date', 'status',
            'address', 'district', 'phone', 'email'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'first_name': 'প্রথম নাম',
            'last_name': 'শেষ নাম',
            'roll_number': 'রোল নং',
            'date_of_birth': 'জন্ম তারিখ',
            'gender': 'লিঙ্গ',
            'blood_group': 'রক্তের গ্রুপ',
            'photo': 'ছবি',
            'grade': 'শ্রেণী',
            'admission_date': 'ভর্তির তারিখ',
            'status': 'অবস্থা',
            'address': 'ঠিকানা',
            'district': 'জেলা',
            'phone': 'ফোন নম্বর',
            'email': 'ইমেইল',
        }
    
    def clean_roll_number(self):
        roll_number = self.cleaned_data.get('roll_number')
        if self.instance.pk:  # Editing existing student
            if Student.objects.filter(roll_number=roll_number).exclude(pk=self.instance.pk).exists():
                raise ValidationError('এই রোল নম্বরটি ইতিমধ্যে ব্যবহৃত হয়েছে')
        else:  # Creating new student
            if Student.objects.filter(roll_number=roll_number).exists():
                raise ValidationError('এই রোল নম্বরটি ইতিমধ্যে ব্যবহৃত হয়েছে')
        return roll_number
    
    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth > timezone.now().date():
            raise ValidationError('জন্ম তারিখ ভবিষ্যতের হতে পারে না')
        return date_of_birth


class GuardianForm(forms.ModelForm):
    class Meta:
        model = Guardian
        fields = ['name', 'relation', 'occupation', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'পূর্ণ নাম',
            'relation': 'শিক্ষার্থীর সাথে সম্পর্ক',
            'occupation': 'পেশা',
            'phone': 'ফোন নম্বর',
            'email': 'ইমেইল',
            'address': 'ঠিকানা',
        }


class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['student', 'month', 'year', 'amount', 'due_date', 'status', 'notes']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'student': 'শিক্ষার্থী',
            'month': 'মাস',
            'year': 'বছর',
            'amount': 'ফির পরিমাণ',
            'due_date': 'পরিশোধের শেষ তারিখ',
            'status': 'অবস্থা',
            'notes': 'মন্তব্য',
        }
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date < timezone.now().date():
            raise ValidationError('পরিশোধের শেষ তারিখ অতীতের হতে পারে না')
        return due_date


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['document_type', 'title', 'file', 'issue_date', 'expiry_date', 'description']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'document_type': 'নথির ধরন',
            'title': 'শিরোনাম',
            'file': 'ফাইল',
            'issue_date': 'ইস্যুর তারিখ',
            'expiry_date': 'মেয়াদ উত্তীর্ণের তারিখ',
            'description': 'বর্ণনা',
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError('ফাইলের আকার 10MB এর বেশি হতে পারবে না')
            
            # Check file extension
            allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
            ext = file.name.split('.')[-1].lower()
            if f'.{ext}' not in allowed_extensions:
                raise ValidationError('শুধুমাত্র PDF, JPG, PNG, DOC, DOCX ফাইল অনুমোদিত')
        
        return file


class AcademicHistoryForm(forms.ModelForm):
    class Meta:
        model = AcademicHistory
        fields = ['academic_year', 'grade', 'section', 'roll_number', 'result', 'status', 'remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'academic_year': 'শিক্ষাবর্ষ',
            'grade': 'শ্রেণী',
            'section': 'বিভাগ',
            'roll_number': 'রোল নং',
            'result': 'ফলাফল',
            'status': 'অবস্থা',
            'remarks': 'মন্তব্য',
        }


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'status', 'remarks']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'student': 'শিক্ষার্থী',
            'date': 'তারিখ',
            'status': 'অবস্থা',
            'remarks': 'মন্তব্য',
        }


class BulkUploadForm(forms.Form):
    file = forms.FileField(
        label='এক্সেল ফাইল',
        help_text='শুধুমাত্র XLSX, XLS, CSV ফাইল অনুমোদিত'
    )


class PromoteStudentsForm(forms.Form):
    current_grade = forms.CharField(max_length=50, label='বর্তমান শ্রেণী')
    current_section = forms.CharField(max_length=10, required=False, label='বর্তমান বিভাগ')
    next_grade = forms.CharField(max_length=50, label='পরবর্তী শ্রেণী')
    next_section = forms.CharField(max_length=10, label='পরবর্তী বিভাগ')
    academic_year = forms.CharField(max_length=9, label='পরবর্তী শিক্ষাবর্ষ')
    update_roll_numbers = forms.BooleanField(required=False, label='রোল নম্বর পুনরায় সেট করুন')