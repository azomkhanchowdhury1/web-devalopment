from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Student, Result

@receiver(post_save, sender=Result)
def update_student_performance(sender, instance, created, **kwargs):
    """
    Update student's overall performance when new results are added
    """
    if created:
        # Calculate average percentage for the student
        student_results = Result.objects.filter(student=instance.student)
        avg_percentage = student_results.aggregate(avg=Avg('percentage'))['avg'] or 0
        
        # You can store this in a StudentProfile model if you have one
        # For now, we'll just log it or you can extend the Student model
        print(f"Student {instance.student.name} now has average: {avg_percentage:.2f}%")