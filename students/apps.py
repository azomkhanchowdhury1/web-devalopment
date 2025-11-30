from django.apps import AppConfig


class StudentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'students'
    verbose_name = 'শিক্ষার্থী ব্যবস্থাপনা'
    
    def ready(self):
        import students.signals