from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import AcademicYear, ClassRoutine

@receiver(post_save, sender=AcademicYear)
def update_active_academic_year(sender, instance, **kwargs):
    """
    Ensure only one academic year is active at a time
    """
    if instance.is_active:
        AcademicYear.objects.exclude(pk=instance.pk).update(is_active=False)

@receiver(post_save, sender=ClassRoutine)
@receiver(post_delete, sender=ClassRoutine)
def clear_routine_cache(sender, **kwargs):
    """
    Clear routine cache when routines are updated or deleted
    """
    # You can implement caching logic here if needed
    pass