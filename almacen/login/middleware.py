"""
Middleware para capturar eventos de seguridad en el módulo de login.
"""

from django.utils.deprecation import MiddlewareMixin
import logging
import re

# Logger específico de seguridad
security_logger = logging.getLogger('security')
login_logger = logging.getLogger('login')


class SecurityMiddleware(MiddlewareMixin):
    """Middleware para detectar y registrar eventos de seguridad."""
    
    def process_request(self, request):
        """Procesa cada request antes de llegar a la vista."""
        # Obtener IP del cliente
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        request.client_ip = ip
        
        # Detectar patrones sospechosos en la URL
        suspicious_patterns = [
            r'\.\./',           # Path traversal
            r'%00',             # Null byte injection
            r'union.*select',   # SQLi
            r'<script',         # XSS
            r'javascript:',     # XSS
            r'onerror=',        # XSS
            r'alert\(',         # XSS
        ]
        
        current_path = request.path
        for pattern in suspicious_patterns:
            if re.search(pattern, current_path, re.IGNORECASE):
                security_logger.warning(
                    f"Patrón sospechoso en URL",
                    extra={
                        'ip': ip,
                        'user': request.user.username if request.user.is_authenticated else 'Anonymous',
                        'event': 'SUSPICIOUS_URL_PATTERN',
                        'details': f"URL: {current_path} | Patrón: {pattern}"
                    }
                )
                break
        
        # Registrar accesos a URLs restringidas sin autenticación
        restricted_paths = ['/login/dashboard/', '/productos/']
        
        if not request.user.is_authenticated and any(current_path.startswith(path) for path in restricted_paths):
            security_logger.warning(
                f"Acceso no autorizado a área restringida",
                extra={
                    'ip': ip,
                    'user': 'Anonymous',
                    'event': 'UNAUTHORIZED_ACCESS_ATTEMPT',
                    'details': f"URL: {current_path} | Método: {request.method}"
                }
            )
            login_logger.warning(f"⚠️ Acceso denegado | IP: {ip} | Intentó acceder a: {current_path}")
    
    def process_response(self, request, response):
        """Procesa la respuesta para detectar errores de seguridad."""
        
        # Detectar errores 403 (Prohibido) y 401 (No autorizado)
        if response.status_code in [401, 403]:
            security_logger.warning(
                f"Error de autorización",
                extra={
                    'ip': getattr(request, 'client_ip', 'unknown'),
                    'user': request.user.username if request.user.is_authenticated else 'Anonymous',
                    'event': 'AUTHORIZATION_ERROR',
                    'details': f"Status: {response.status_code} | URL: {request.path}"
                }
            )
        
        # Detectar errores 404 que podrían ser escaneo
        if response.status_code == 404:
            login_logger.info(f"🔍 404 - Recurso no encontrado | IP: {getattr(request, 'client_ip', 'unknown')} | URL: {request.path}")
        
        return response