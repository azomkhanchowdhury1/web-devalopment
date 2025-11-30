from django.apps import AppConfig

class AttendanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'attendance'
    verbose_name = 'উপস্থিতি ব্যবস্থাপনা'
    
    def ready(self):
        import attendance.signals