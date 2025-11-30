from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Student, AcademicHistory, Fee
from django.utils import timezone


@receiver(post_save, sender=Student)
def create_initial_academic_history(sender, instance, created, **kwargs):
    if created:
        # Create initial academic history record
        AcademicHistory.objects.create(
            student=instance,
            academic_year=f"{instance.admission_date.year}-{instance.admission_date.year + 1}",
            grade=instance.grade.name,
            section=instance.grade.section,
            roll_number=instance.roll_number,
            status=instance.status,
            remarks="প্রাথমিক ভর্তি"
        )


@receiver(post_save, sender=Student)
def update_fee_status(sender, instance, **kwargs):
    if instance.status != 'Active':
        # Mark all pending fees as cancelled for inactive students
        Fee.objects.filter(
            student=instance,
            status__in=['Pending', 'Partial']
        ).update(status='Cancelled')


@receiver(pre_delete, sender=Student)
def delete_associated_records(sender, instance, **kwargs):
    # Delete associated records when student is deleted
    # You might want to implement soft delete instead
    pass