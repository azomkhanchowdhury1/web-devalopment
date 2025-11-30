from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Class(models.Model):
    CLASS_CHOICES = [
        (6, 'ষষ্ঠ শ্রেণী'),
        (7, 'সপ্তম শ্রেণী'),
        (8, 'অষ্টম শ্রেণী'),
        (9, 'নবম শ্রেণী'),
        (10, 'দশম শ্রেণী'),
    ]
    
    class_name = models.IntegerField(choices=CLASS_CHOICES, verbose_name="শ্রেণী")
    section = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C')], verbose_name="শাখা")
    
    class Meta:
        verbose_name = "শ্রেণী"
        verbose_name_plural = "শ্রেণীসমূহ"
        unique_together = ['class_name', 'section']
    
    def __str__(self):
        return f"{self.class_name} - {self.section}"

class Subject(models.Model):
    SUBJECT_CHOICES = [
        ('bangla', 'বাংলা'),
        ('english', 'ইংরেজি'),
        ('math', 'গণিত'),
        ('science', 'বিজ্ঞান'),
        ('social_science', 'সামাজিক বিজ্ঞান'),
        ('religion', 'ধর্ম'),
        ('ict', 'তথ্য ও যোগাযোগ প্রযুক্তি'),
    ]
    
    name = models.CharField(max_length=50, choices=SUBJECT_CHOICES, verbose_name="বিষয়ের নাম")
    code = models.CharField(max_length=10, unique=True, verbose_name="বিষয় কোড")
    
    class Meta:
        verbose_name = "বিষয়"
        verbose_name_plural = "বিষয়সমূহ"
    
    def __str__(self):
        return self.get_name_display()

class Student(models.Model):
    GENDER_CHOICES = [
        ('M', 'পুরুষ'),
        ('F', 'মহিলা'),
    ]
    
    student_id = models.CharField(max_length=20, unique=True, verbose_name="শিক্ষার্থী আইডি")
    roll_number = models.IntegerField(verbose_name="রোল নং")
    name = models.CharField(max_length=100, verbose_name="পূর্ণ নাম")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="লিঙ্গ")
    date_of_birth = models.DateField(verbose_name="জন্ম তারিখ")
    class_info = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="শ্রেণী")
    address = models.TextField(verbose_name="ঠিকানা")
    phone = models.CharField(max_length=15, blank=True, verbose_name="ফোন নম্বর")
    email = models.EmailField(blank=True, verbose_name="ইমেইল")
    guardian_name = models.CharField(max_length=100, verbose_name="অভিভাবকের নাম")
    guardian_phone = models.CharField(max_length=15, verbose_name="অভিভাবকের ফোন")
    photo = models.ImageField(upload_to='students/', blank=True, null=True, verbose_name="ছবি")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "শিক্ষার্থী"
        verbose_name_plural = "শিক্ষার্থীবৃন্দ"
        unique_together = ['class_info', 'roll_number']
    
    def __str__(self):
        return f"{self.name} - {self.class_info}"

class Attendance(models.Model):
    PERIOD_CHOICES = [
        (1, '১ম পিরিয়ড'),
        (2, '২য় পিরিয়ড'),
        (3, '৩য় পিরিয়ড'),
        (4, '৪র্থ পিরিয়ড'),
        (5, '৫ম পিরিয়ড'),
        (6, '৬ষ্ঠ পিরিয়ড'),
    ]
    
    class_info = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name="শ্রেণী")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="বিষয়")
    date = models.DateField(verbose_name="তারিখ")
    period = models.IntegerField(choices=PERIOD_CHOICES, verbose_name="পিরিয়ড")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="শিক্ষক", related_name='attendance_teacher')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "উপস্থিতি"
        verbose_name_plural = "উপস্থিতি রেকর্ড"
        unique_together = ['class_info', 'subject', 'date', 'period']
    
    def __str__(self):
        return f"{self.class_info} - {self.subject} - {self.date}"
    
    @property
    def total_students(self):
        return self.attendance_records.count()
    
    @property
    def present_count(self):
        return self.attendance_records.filter(status='present').count()
    
    @property
    def absent_count(self):
        return self.attendance_records.filter(status='absent').count()
    
    @property
    def attendance_percentage(self):
        if self.total_students > 0:
            return round((self.present_count / self.total_students) * 100, 2)
        return 0

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('present', 'উপস্থিত'),
        ('absent', 'অনুপস্থিত'),
        ('late', 'দেরীতে উপস্থিত'),
        ('excused', 'ছুটি প্রাপ্ত'),
    ]
    
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="শিক্ষার্থী")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present', verbose_name="স্ট্যাটাস")
    remarks = models.CharField(max_length=200, blank=True, verbose_name="মন্তব্য")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "উপস্থিতি রেকর্ড"
        verbose_name_plural = "উপস্থিতি রেকর্ডসমূহ"
        unique_together = ['attendance', 'student']
    
    def __str__(self):
        return f"{self.student.name} - {self.attendance.date} - {self.get_status_display()}"

class MonthlyReport(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name="শিক্ষার্থী")
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)], verbose_name="মাস")
    year = models.IntegerField(verbose_name="বছর")
    total_days = models.IntegerField(default=0, verbose_name="মোট দিন")
    present_days = models.IntegerField(default=0, verbose_name="উপস্থিত দিন")
    absent_days = models.IntegerField(default=0, verbose_name="অনুপস্থিত দিন")
    late_days = models.IntegerField(default=0, verbose_name="দেরীতে উপস্থিত দিন")
    attendance_percentage = models.FloatField(default=0, verbose_name="উপস্থিতির হার")
    
    class Meta:
        verbose_name = "মাসিক রিপোর্ট"
        verbose_name_plural = "মাসিক রিপোর্টসমূহ"
        unique_together = ['student', 'month', 'year']
    
    def __str__(self):
        return f"{self.student.name} - {self.month}/{self.year}"
    
    def save(self, *args, **kwargs):
        if self.total_days > 0:
            self.attendance_percentage = round((self.present_days / self.total_days) * 100, 2)
        super().save(*args, **kwargs)