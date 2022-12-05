from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"
    verbose_name = _("White Bridge Club")
    verbose_name_plural = _("White Bridge Club")
    
    def ready(self):
        import api.signals
