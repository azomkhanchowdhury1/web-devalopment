from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Teacher, ClassSchedule, Assignment, Attendance, StudentResult, Notice

User = get_user_model()

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=True, label="নাম")
    last_name = forms.CharField(max_length=100, required=True, label="উপাধি")
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'name', 'email', 'phone', 'subject', 'joining_date', 
            'salary', 'address', 'photo', 'qualification', 
            'experience', 'is_active'
        ]
        widgets = {
            'joining_date': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'qualification': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'name': 'পুরো নাম',
            'email': 'ইমেইল',
            'phone': 'ফোন নম্বর',
            'subject': 'বিষয়',
            'joining_date': 'যোগদানের তারিখ',
            'salary': 'বেতন',
            'address': 'ঠিকানা',
            'photo': 'ছবি',
            'qualification': 'শিক্ষাগত যোগ্যতা',
            'experience': 'অভিজ্ঞতা (বছর)',
            'is_active': 'সক্রিয়',
        }

class ClassScheduleForm(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['class_name', 'subject', 'day', 'start_time', 'end_time', 'room']
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }
        labels = {
            'class_name': 'ক্লাস',
            'subject': 'বিষয়',
            'day': 'দিন',
            'start_time': 'শুরু সময়',
            'end_time': 'শেষ সময়',
            'room': 'রুম নম্বর',
        }

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'class_name', 'subject', 'due_date', 'total_marks', 'file']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'শিরোনাম',
            'description': 'বর্ণনা',
            'class_name': 'ক্লাস',
            'subject': 'বিষয়',
            'due_date': 'জমা দেওয়ার শেষ তারিখ',
            'total_marks': 'মোট নম্বর',
            'file': 'ফাইল',
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['class_name', 'subject', 'date', 'total_students', 'present_students', 'absent_students']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'class_name': 'ক্লাস',
            'subject': 'বিষয়',
            'date': 'তারিখ',
            'total_students': 'মোট শিক্ষার্থী',
            'present_students': 'উপস্থিত শিক্ষার্থী',
            'absent_students': 'অনুপস্থিত শিক্ষার্থী',
        }

class StudentResultForm(forms.ModelForm):
    class Meta:
        model = StudentResult
        fields = ['student_name', 'student_roll', 'class_name', 'subject', 'exam_type', 'marks', 'total_marks', 'grade', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'student_name': 'শিক্ষার্থীর নাম',
            'student_roll': 'রোল নম্বর',
            'class_name': 'ক্লাস',
            'subject': 'বিষয়',
            'exam_type': 'পরীক্ষার ধরন',
            'marks': 'প্রাপ্ত নম্বর',
            'total_marks': 'মোট নম্বর',
            'grade': 'গ্রেড',
            'comments': 'মন্তব্য',
        }

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'priority', 'target_class', 'is_published']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'title': 'শিরোনাম',
            'content': 'বিস্তারিত',
            'priority': 'অগ্রাধিকার',
            'target_class': 'লক্ষ্য ক্লাস',
            'is_published': 'প্রকাশিত',
        }