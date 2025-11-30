from django import forms
from .models import Result, Student, Class, Subject, GradeSystem

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'student_class', 'subject', 'exam_type', 'marks_obtained', 'total_marks', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'exam_type': forms.Select(attrs={'class': 'form-select'}),
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.all().order_by('name')
        self.fields['student_class'].queryset = Class.objects.all().order_by('name')
        self.fields['subject'].queryset = Subject.objects.all().order_by('name')

class BulkResultUploadForm(forms.Form):
    class_choice = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    subject_choice = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    exam_type = forms.ChoiceField(
        choices=Result.EXAM_TYPES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )

class ResultFilterForm(forms.Form):
    class_filter = forms.ModelChoiceField(
        queryset=Class.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    exam_filter = forms.ChoiceField(
        choices=[('', 'All Exams')] + list(Result.EXAM_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    student_filter = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class GradeSystemForm(forms.ModelForm):
    class Meta:
        model = GradeSystem
        fields = ['grade', 'min_percentage', 'max_percentage', 'gpa', 'description']
        widgets = {
            'grade': forms.TextInput(attrs={'class': 'form-control'}),
            'min_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }