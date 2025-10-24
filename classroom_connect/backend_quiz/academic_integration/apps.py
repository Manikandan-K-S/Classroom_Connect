from django.apps import AppConfig


class AcademicIntegrationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "academic_integration"
    
    def ready(self):
        """Import signals when the app is ready."""
        import academic_integration.signals
