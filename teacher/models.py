from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Teacher(models.Model):
    SUBJECT_CHOICES = [
        ('bangla', 'বাংলা'),
        ('english', 'ইংরেজি'),
        ('math', 'গণিত'),
        ('science', 'বিজ্ঞান'),
        ('social_science', 'সামাজিক বিজ্ঞান'),
        ('religion', 'ধর্ম'),
        ('ict', 'তথ্য ও যোগাযোগ প্রযুক্তি'),
        ('physics', 'পদার্থবিজ্ঞান'),
        ('chemistry', 'রসায়ন'),
        ('biology', 'জীববিজ্ঞান'),
        ('accounting', 'হিসাববিজ্ঞান'),
        ('finance', 'ফিন্যান্স'),
    ]
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='teacher')
    name = models.CharField(max_length=100, verbose_name="পুরো নাম")
    email = models.EmailField(unique=True, verbose_name="ইমেইল")
    phone = models.CharField(max_length=15, verbose_name="ফোন নম্বর")
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, verbose_name="বিষয়")
    joining_date = models.DateField(verbose_name="যোগদানের তারিখ")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="বেতন")
    address = models.TextField(verbose_name="ঠিকানা")
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True, verbose_name="ছবি")
    qualification = models.TextField(verbose_name="শিক্ষাগত যোগ্যতা")
    experience = models.FloatField(default=0, verbose_name="অভিজ্ঞতা (বছর)")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "শিক্ষক"
        verbose_name_plural = "শিক্ষকবৃন্দ"
        ordering = ['-joining_date']
    
    def __str__(self):
        return self.name

class ClassSchedule(models.Model):
    DAY_CHOICES = [
        ('saturday', 'শনিবার'),
        ('sunday', 'রবিবার'),
        ('monday', 'সোমবার'),
        ('tuesday', 'মঙ্গলবার'),
        ('wednesday', 'বুধবার'),
        ('thursday', 'বৃহস্পতিবার'),
        ('friday', 'শুক্রবার'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedules')
    class_name = models.CharField(max_length=50, verbose_name="ক্লাস")
    subject = models.CharField(max_length=50, verbose_name="বিষয়")
    day = models.CharField(max_length=10, choices=DAY_CHOICES, verbose_name="দিন")
    start_time = models.TimeField(verbose_name="শুরু সময়")
    end_time = models.TimeField(verbose_name="শেষ সময়")
    room = models.CharField(max_length=20, verbose_name="রুম নম্বর")
    
    class Meta:
        verbose_name = "ক্লাস সিডিউল"
        verbose_name_plural = "ক্লাস সিডিউল"
        ordering = ['day', 'start_time']
    
    def __str__(self):
        return f"{self.class_name} - {self.subject} - {self.day}"

class Assignment(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200, verbose_name="শিরোনাম")
    description = models.TextField(verbose_name="বর্ণনা")
    class_name = models.CharField(max_length=50, verbose_name="ক্লাস")
    subject = models.CharField(max_length=50, verbose_name="বিষয়")
    due_date = models.DateTimeField(verbose_name="জমা দেওয়ার শেষ তারিখ")
    total_marks = models.IntegerField(default=100, verbose_name="মোট নম্বর")
    file = models.FileField(upload_to='assignments/', blank=True, null=True, verbose_name="ফাইল")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "এসাইনমেন্ট"
        verbose_name_plural = "এসাইনমেন্টসমূহ"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Attendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='attendances')
    class_name = models.CharField(max_length=50, verbose_name="ক্লাস")
    subject = models.CharField(max_length=50, verbose_name="বিষয়")
    date = models.DateField(verbose_name="তারিখ")
    total_students = models.IntegerField(default=0, verbose_name="মোট শিক্ষার্থী")
    present_students = models.IntegerField(default=0, verbose_name="উপস্থিত শিক্ষার্থী")
    absent_students = models.IntegerField(default=0, verbose_name="অনুপস্থিত শিক্ষার্থী")
    
    class Meta:
        verbose_name = "উপস্থিতি"
        verbose_name_plural = "উপস্থিতির রেকর্ড"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.class_name} - {self.date}"

class StudentResult(models.Model):
    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('B-', 'B-'),
        ('C+', 'C+'),
        ('C', 'C'),
        ('D', 'D'),
        ('F', 'F'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='results')
    student_name = models.CharField(max_length=100, verbose_name="শিক্ষার্থীর নাম")
    student_roll = models.CharField(max_length=20, verbose_name="রোল নম্বর")
    class_name = models.CharField(max_length=50, verbose_name="ক্লাস")
    subject = models.CharField(max_length=50, verbose_name="বিষয়")
    exam_type = models.CharField(max_length=50, verbose_name="পরীক্ষার ধরন")
    marks = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="প্রাপ্ত নম্বর")
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100, verbose_name="মোট নম্বর")
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, verbose_name="গ্রেড")
    comments = models.TextField(blank=True, verbose_name="মন্তব্য")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "ফলাফল"
        verbose_name_plural = "ফলাফলসমূহ"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student_name} - {self.subject} - {self.grade}"

class Notice(models.Model):
    PRIORITY_CHOICES = [
        ('high', 'উচ্চ'),
        ('medium', 'মধ্যম'),
        ('low', 'নিম্ন'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='notices')
    title = models.CharField(max_length=200, verbose_name="শিরোনাম")
    content = models.TextField(verbose_name="বিস্তারিত")
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name="অগ্রাধিকার")
    target_class = models.CharField(max_length=50, blank=True, verbose_name="লক্ষ্য ক্লাস")
    is_published = models.BooleanField(default=False, verbose_name="প্রকাশিত")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "নোটিশ"
        verbose_name_plural = "নোটিশসমূহ"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title