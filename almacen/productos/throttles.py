"""
Throttling personalizado para rate limiting en la API.
"""

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
import logging

security_logger = logging.getLogger('security')


class APIUserRateThrottle(UserRateThrottle):
    """Límite de requests para usuarios autenticados: 100/minuto."""
    scope = 'api_user'
    
    def throttle_success(self):
        return super().throttle_success()
    
    def throttle_failure(self):
        """Registra intento de rate limiting excedido."""
        security_logger.warning(
            f"🚨 FUERZA BRUTA DETECTADA | Usuario: {self.request.user.username if self.request.user.is_authenticated else 'Anónimo'} | "
            f"IP: {self.get_ident()} | Intentos excedidos (>100/min)"
        )
        return super().throttle_failure()


class APIAnonRateThrottle(AnonRateThrottle):
    """Límite de requests para usuarios anónimos: 20/minuto."""
    scope = 'api_anon'
    
    def throttle_failure(self):
        """Registra intento de rate limiting excedido."""
        security_logger.warning(
            f"🚨 FUERZA BRUTA DETECTADA | Usuario: Anónimo | "
            f"IP: {self.get_ident()} | Intentos excedidos (>20/min)"
        )
        return super().throttle_failure()
