from django.apps import AppConfig
import logging

logger = logging.getLogger('login')

class LoginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'login'
    verbose_name = 'Módulo de Autenticación'
    
    def ready(self):
        """
        Se ejecuta cuando la app está lista
        """
        logger.info("✅ Módulo de login cargado correctamente")