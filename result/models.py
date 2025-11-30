from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Class(models.Model):
    name = models.CharField(max_length=50)
    section = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} {self.section}" if self.section else self.name
    
    class Meta:
        verbose_name_plural = "Classes"

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    class_associated = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects')
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    father_name = models.CharField(max_length=100)
    mother_name = models.CharField(max_length=100)
    address = models.TextField()
    phone = models.CharField(max_length=15)
    current_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='students')
    section = models.CharField(max_length=10)
    profile_picture = models.ImageField(upload_to='student_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.roll_number})"

class Result(models.Model):
    EXAM_TYPES = (
        ('midterm', 'Midterm Exam'),
        ('final', 'Final Exam'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
    )
    
    GRADES = (
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='results')
    student_class = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='results')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='results')
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(1)])
    percentage = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    grade = models.CharField(max_length=2, choices=GRADES)
    gpa = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(5)])
    remarks = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'exam_type']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.get_exam_type_display()}"
    
    def save(self, *args, **kwargs):
        # Calculate percentage
        self.percentage = (self.marks_obtained / self.total_marks) * 100
        
        # Calculate grade and GPA based on percentage
        if self.percentage >= 80:
            self.grade = 'A+'
            self.gpa = 5.00
        elif self.percentage >= 70:
            self.grade = 'A'
            self.gpa = 4.00
        elif self.percentage >= 60:
            self.grade = 'A-'
            self.gpa = 3.50
        elif self.percentage >= 50:
            self.grade = 'B'
            self.gpa = 3.00
        elif self.percentage >= 40:
            self.grade = 'C'
            self.gpa = 2.00
        elif self.percentage >= 33:
            self.grade = 'D'
            self.gpa = 1.00
        else:
            self.grade = 'F'
            self.gpa = 0.00
            
        super().save(*args, **kwargs)

class GradeSystem(models.Model):
    grade = models.CharField(max_length=2, unique=True)
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    gpa = models.DecimalField(max_digits=3, decimal_places=2)
    description = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.grade} (GPA: {self.gpa})"