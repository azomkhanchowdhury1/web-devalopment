from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class AcademicYear(models.Model):
    year = models.CharField(max_length=9, unique=True, help_text="Format: YYYY-YYYY")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        ordering = ['-year']

    def __str__(self):
        return self.year

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate all other academic years
            AcademicYear.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

class Subject(models.Model):
    SUBJECT_TYPES = [
        ('core', 'Core Subject'),
        ('elective', 'Elective Subject'),
        ('extra', 'Extra Curricular'),
    ]

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    subject_type = models.CharField(max_length=20, choices=SUBJECT_TYPES, default='core')
    description = models.TextField(blank=True)
    credit_hours = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

class Class(models.Model):
    name = models.CharField(max_length=50, unique=True)
    section = models.CharField(max_length=10, blank=True)
    class_teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        limit_choices_to={'groups__name': 'Teachers'}
    )
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, null=True)
    capacity = models.PositiveIntegerField(default=40)
    subjects = models.ManyToManyField(Subject, through='ClassSubject')
    room_number = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ['name']
        unique_together = ['name', 'academic_year']

    def __str__(self):
        if self.section:
            return f"{self.name} - {self.section}"
        return self.name

    @property
    def student_count(self):
        return self.student_set.count()

class ClassSubject(models.Model):
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        limit_choices_to={'groups__name': 'Teachers'}
    )
    is_compulsory = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Class Subject"
        verbose_name_plural = "Class Subjects"
        unique_together = ['class_obj', 'subject']

    def __str__(self):
        return f"{self.class_obj} - {self.subject}"

class ClassRoutine(models.Model):
    DAYS_OF_WEEK = [
        ('sunday', 'Sunday'),
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
        ('saturday', 'Saturday'),
    ]

    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    period = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Teachers'}
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Class Routine"
        verbose_name_plural = "Class Routines"
        ordering = ['class_obj', 'day', 'period']
        unique_together = ['class_obj', 'day', 'period']

    def __str__(self):
        return f"{self.class_obj} - {self.get_day_display()} - Period {self.period}"

    def duration(self):
        from datetime import datetime
        start = datetime.strptime(str(self.start_time), '%H:%M:%S')
        end = datetime.strptime(str(self.end_time), '%H:%M:%S')
        duration = end - start
        minutes = duration.total_seconds() / 60
        return f"{int(minutes)} minutes"