from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
import os
from django.utils import timezone


class Grade(models.Model):
    name = models.CharField(max_length=50, verbose_name="শ্রেণীর নাম")
    section = models.CharField(max_length=10, verbose_name="বিভাগ", blank=True, null=True)
    capacity = models.IntegerField(verbose_name="ধারণক্ষমতা", default=40)
    
    class Meta:
        verbose_name = "শ্রেণী"
        verbose_name_plural = "শ্রেণীসমূহ"
        unique_together = ['name', 'section']
    
    def __str__(self):
        if self.section:
            return f"{self.name} - {self.section}"
        return self.name
    
    def student_count(self):
        return self.student_set.filter(status='Active').count()
    
    def available_seats(self):
        return self.capacity - self.student_count()


class Guardian(models.Model):
    RELATION_CHOICES = [
        ('Father', 'পিতা'),
        ('Mother', 'মাতা'),
        ('Brother', 'ভাই'),
        ('Sister', 'বোন'),
        ('Grandfather', 'দাদা/নানা'),
        ('Grandmother', 'দাদী/নানী'),
        ('Uncle', 'চাচা/মামা'),
        ('Aunt', 'চাচী/মামী'),
        ('Other', 'অন্যান্য'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="নাম")
    relation = models.CharField(max_length=20, choices=RELATION_CHOICES, verbose_name="সম্পর্ক")
    occupation = models.CharField(max_length=100, verbose_name="পেশা", blank=True, null=True)
    phone = models.CharField(max_length=15, verbose_name="ফোন নম্বর")
    email = models.EmailField(verbose_name="ইমেইল", blank=True, null=True)
    address = models.TextField(verbose_name="ঠিকানা")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "অভিভাবক"
        verbose_name_plural = "অভিভাবকগণ"
    
    def __str__(self):
        return f"{self.name} ({self.relation})"


def student_photo_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"student_{instance.roll_number}_{instance.id}.{ext}"
    return os.path.join('students/photos/', filename)


class Student(models.Model):
    GENDER_CHOICES = [
        ('Male', 'পুরুষ'),
        ('Female', 'মহিলা'),
        ('Other', 'অন্যান্য'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    
    STATUS_CHOICES = [
        ('Active', 'সক্রিয়'),
        ('Inactive', 'নিষ্ক্রিয়'),
        ('Transferred', 'স্থানান্তরিত'),
        ('Graduated', 'পাস আউট'),
    ]
    
    # Personal Information
    first_name = models.CharField(max_length=50, verbose_name="প্রথম নাম")
    last_name = models.CharField(max_length=50, verbose_name="শেষ নাম")
    roll_number = models.CharField(max_length=20, unique=True, verbose_name="রোল নং")
    date_of_birth = models.DateField(verbose_name="জন্ম তারিখ")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="লিঙ্গ")
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, verbose_name="রক্তের গ্রুপ", blank=True, null=True)
    photo = models.ImageField(upload_to=student_photo_path, verbose_name="ছবি", blank=True, null=True)
    
    # Academic Information
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, verbose_name="শ্রেণী")
    admission_date = models.DateField(verbose_name="ভর্তির তারিখ", default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active', verbose_name="অবস্থা")
    
    # Contact Information
    address = models.TextField(verbose_name="ঠিকানা")
    district = models.CharField(max_length=50, verbose_name="জেলা")
    phone = models.CharField(max_length=15, verbose_name="ফোন নম্বর", blank=True, null=True)
    email = models.EmailField(verbose_name="ইমেইল", blank=True, null=True)
    
    # Guardian Information
    guardian = models.ForeignKey(Guardian, on_delete=models.SET_NULL, verbose_name="অভিভাবক", null=True, blank=True)
    
    # System Fields
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='students_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "শিক্ষার্থী"
        verbose_name_plural = "শিক্ষার্থীগণ"
        ordering = ['grade', 'roll_number']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.roll_number})"
    
    def get_absolute_url(self):
        return reverse('student_detail', kwargs={'pk': self.pk})
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def age(self):
        today = timezone.now().date()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )
    
    def current_grade(self):
        return f"{self.grade.name} {self.grade.section if self.grade.section else ''}".strip()


class AcademicHistory(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="শিক্ষার্থী")
    academic_year = models.CharField(max_length=9, verbose_name="শিক্ষাবর্ষ")  # Format: 2023-2024
    grade = models.CharField(max_length=50, verbose_name="শ্রেণী")
    section = models.CharField(max_length=10, verbose_name="বিভাগ", blank=True, null=True)
    roll_number = models.CharField(max_length=20, verbose_name="রোল নং")
    result = models.CharField(max_length=50, verbose_name="ফলাফল", blank=True, null=True)
    status = models.CharField(max_length=20, choices=Student.STATUS_CHOICES, verbose_name="অবস্থা")
    remarks = models.TextField(verbose_name="মন্তব্য", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "একাডেমিক ইতিহাস"
        verbose_name_plural = "একাডেমিক ইতিহাস"
        ordering = ['-academic_year', 'grade']
    
    def __str__(self):
        return f"{self.student} - {self.academic_year} ({self.grade})"


class Fee(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'বকেয়া'),
        ('Partial', 'আংশিক পরিশোধিত'),
        ('Paid', 'পরিশোধিত'),
        ('Overdue', 'মেয়াদোত্তীর্ণ'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="শিক্ষার্থী")
    month = models.CharField(max_length=20, verbose_name="মাস")
    year = models.IntegerField(verbose_name="বছর", validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="ফির পরিমাণ")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="পরিশোধিত পরিমাণ", default=0)
    due_date = models.DateField(verbose_name="পরিশোধের শেষ তারিখ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending', verbose_name="অবস্থা")
    notes = models.TextField(verbose_name="মন্তব্য", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "ফি"
        verbose_name_plural = "ফি"
        unique_together = ['student', 'month', 'year']
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.student} - {self.month} {self.year}"
    
    def due_amount(self):
        return self.amount - self.paid_amount
    
    def is_overdue(self):
        return timezone.now().date() > self.due_date and self.status != 'Paid'


def document_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"doc_{instance.student.roll_number}_{instance.document_type}_{instance.id}.{ext}"
    return os.path.join('students/documents/', filename)


class Document(models.Model):
    DOCUMENT_TYPES = [
        ('Birth_Certificate', 'জন্ম নিবন্ধন'),
        ('NID', 'জাতীয় পরিচয়পত্র'),
        ('Photo', 'ছবি'),
        ('Transcript', 'ট্রান্সক্রিপ্ট'),
        ('Certificate', 'সনদপত্র'),
        ('Medical', 'মেডিকেল রিপোর্ট'),
        ('Other', 'অন্যান্য'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="শিক্ষার্থী")
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, verbose_name="নথির ধরন")
    title = models.CharField(max_length=200, verbose_name="শিরোনাম")
    file = models.FileField(upload_to=document_file_path, verbose_name="ফাইল")
    issue_date = models.DateField(verbose_name="ইস্যুর তারিখ", blank=True, null=True)
    expiry_date = models.DateField(verbose_name="মেয়াদ উত্তীর্ণের তারিখ", blank=True, null=True)
    description = models.TextField(verbose_name="বর্ণনা", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "নথি"
        verbose_name_plural = "নথিপত্র"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.student} - {self.title}"
    
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()
    
    def is_image(self):
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        return self.file_extension() in image_extensions


class Attendance(models.Model):
    STATUS_CHOICES = [
        ('Present', 'উপস্থিত'),
        ('Absent', 'অনুপস্থিত'),
        ('Late', 'দেরী'),
        ('Halfday', 'অর্ধদিবস'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="শিক্ষার্থী")
    date = models.DateField(verbose_name="তারিখ", default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="অবস্থা")
    remarks = models.CharField(max_length=200, verbose_name="মন্তব্য", blank=True, null=True)
    marked_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name="চিহ্নিতকারী", related_name='student_attendance_marked_by')
    marked_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "উপস্থিতি"
        verbose_name_plural = "উপস্থিতি রেকর্ড"
        unique_together = ['student', 'date']
        ordering = ['-date', 'student']
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.status}"