from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Teacher

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_teacher_profile(sender, instance, created, **kwargs):
    if created and hasattr(instance, 'teacher_registration'):
        Teacher.objects.create(
            user=instance,
            name=f"{instance.first_name} {instance.last_name}",
            email=instance.email
        )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_teacher_profile(sender, instance, **kwargs):
    if hasattr(instance, 'teacher'):
        instance.teacher.save()