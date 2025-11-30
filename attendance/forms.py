from django import forms
from .models import Attendance, AttendanceRecord, Student, Class, Subject
from django.contrib.auth.models import User

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['class_info', 'subject', 'date', 'period']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'class_info': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'period': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'class_info': 'শ্রেণী',
            'subject': 'বিষয়',
            'date': 'তারিখ',
            'period': 'পিরিয়ড',
        }

class AttendanceRecordForm(forms.ModelForm):
    class Meta:
        model = AttendanceRecord
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'মন্তব্য (ঐচ্ছিক)'}),
        }
        labels = {
            'status': 'স্ট্যাটাস',
            'remarks': 'মন্তব্য',
        }

class AttendanceFilterForm(forms.Form):
    class_name = forms.ChoiceField(
        choices=[('', 'সব শ্রেণী')] + list(Class.CLASS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='শ্রেণী'
    )
    section = forms.ChoiceField(
        choices=[('', 'সব শাখা')] + list(Class._meta.get_field('section').choices),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='শাখা'
    )
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='তারিখ'
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        required=False,
        empty_label="সব বিষয়",
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='বিষয়'
    )

class StudentAttendanceFilterForm(forms.Form):
    month = forms.ChoiceField(
        choices=[
            (1, 'জানুয়ারি'), (2, 'ফেব্রুয়ারি'), (3, 'মার্চ'), (4, 'এপ্রিল'),
            (5, 'মে'), (6, 'জুন'), (7, 'জুলাই'), (8, 'আগস্ট'),
            (9, 'সেপ্টেম্বর'), (10, 'অক্টোবর'), (11, 'নভেম্বর'), (12, 'ডিসেম্বর')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='মাস'
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'বছর'}),
        label='বছর'
    )

class BulkAttendanceForm(forms.Form):
    class_info = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='শ্রেণী'
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='বিষয়'
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='তারিখ'
    )
    period = forms.ChoiceField(
        choices=Attendance.PERIOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='পিরিয়ড'
    )
    status = forms.ChoiceField(
        choices=[('present', 'সবাই উপস্থিত'), ('absent', 'সবাই অনুপস্থিত')],
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='ডিফল্ট স্ট্যাটাস'
    )