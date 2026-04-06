from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.core.cache import cache
from django.conf import settings
from .forms import CustomLoginForm
import logging
import traceback
import uuid
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger('login')
security_logger = logging.getLogger('security')

# Diccionario para almacenar intentos de login fallidos por IP (en producción usar Redis/cache)
# Usaremos cache de Django que por defecto es en memoria
FAILED_LOGIN_KEY = 'failed_login_{ip}'
BLOCKED_IP_KEY = 'blocked_ip_{ip}'


def get_client_ip(request):
    """Obtiene la IP real del cliente."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def is_ip_blocked(ip):
    """Verifica si una IP está bloqueada."""
    return cache.get(BLOCKED_IP_KEY.format(ip=ip), False)


def register_failed_attempt(ip, username):
    """Registra un intento fallido y verifica bloqueo."""
    key = FAILED_LOGIN_KEY.format(ip=ip)
    attempts = cache.get(key, [])
    
    # Limpiar intentos antiguos (más de 5 minutos)
    now = datetime.now()
    attempts = [a for a in attempts if now - a['timestamp'] < timedelta(minutes=5)]
    
    # Agregar nuevo intento
    attempts.append({
        'timestamp': now,
        'username': username
    })
    
    # Guardar en cache por 10 minutos
    cache.set(key, attempts, 600)
    
    # Verificar si debe bloquear (5 intentos en 5 minutos)
    if len(attempts) >= 5:
        cache.set(BLOCKED_IP_KEY.format(ip=ip), True, 900)  # Bloquear por 15 minutos
        return True
    
    return False


def log_request_metadata(view_func):
    """Decorador para registrar metadatos de la solicitud"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        request.request_id = str(uuid.uuid4())[:8]
        
        logger.info(
            f"[RequestID: {request.request_id}] Inicio de solicitud | "
            f"Método: {request.method} | Ruta: {request.path} | IP: {get_client_ip(request)}"
        )
        
        try:
            response = view_func(request, *args, **kwargs)
            logger.info(
                f"[RequestID: {request.request_id}] Solicitud completada | "
                f"Status: {response.status_code}"
            )
            return response
        except Exception as e:
            logger.critical(
                f"[RequestID: {request.request_id}] Error en vista: {str(e)}\n"
                f"{traceback.format_exc()}"
            )
            raise
    return wrapper


def login_view(request):
    """Vista de login con detección de fuerza bruta y logging de seguridad."""
    
    # Obtener IP del cliente
    client_ip = get_client_ip(request)
    
    # Verificar si la IP está bloqueada
    if is_ip_blocked(client_ip):
        security_logger.critical(
            f"IP bloqueada intentando acceder",
            extra={
                'ip': client_ip,
                'user': 'Anonymous',
                'event': 'BLOCKED_IP_ACCESS_ATTEMPT',
                'details': f"IP bloqueada por múltiples intentos fallidos"
            }
        )
        messages.error(request, 'Demasiados intentos fallidos. Intente más tarde.')
        return render(request, 'login/login.html', {'form': CustomLoginForm()})
    
    # Si ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        logger.info(f"Usuario autenticado {request.user.username} intenta acceder a login | Redirigiendo a dashboard | IP: {client_ip}")
        return redirect('/login/dashboard/')
    
    form = CustomLoginForm()
    
    if request.method == 'POST':
        logger.info("=== INICIO OPERACIÓN LOGIN ===")
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        # Detectar inputs sospechosos (posible inyección)
        suspicious_inputs = ['<script', 'javascript:', 'union select', 'drop table', '--', "';"]
        for suspicious in suspicious_inputs:
            if suspicious in username.lower() or suspicious in password.lower():
                security_logger.critical(
                    f"Posible inyección detectada en login",
                    extra={
                        'ip': client_ip,
                        'user': 'Anonymous',
                        'event': 'POSSIBLE_INJECTION_ATTACK',
                        'details': f"Campo: username | Input: {username[:50]} | Patrón: {suspicious}"
                    }
                )
                messages.error(request, 'Datos inválidos')
                return render(request, 'login/login.html', {'form': form})
        
        logger.info(f"Intento de autenticación para usuario: {username} | IP: {client_ip}")
        
        try:
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # Login exitoso
                login(request, user)
                
                # Limpiar intentos fallidos de esta IP al loguearse exitosamente
                cache.delete(FAILED_LOGIN_KEY.format(ip=client_ip))
                
                logger.info(f"✅ LOGIN EXITOSO | Usuario: {username} | ID: {user.id} | IP: {client_ip}")
                
                # Log de seguridad para login exitoso
                security_logger.info(
                    f"Login exitoso",
                    extra={
                        'ip': client_ip,
                        'user': username,
                        'event': 'SUCCESSFUL_LOGIN',
                        'details': f"User ID: {user.id} | User agent: {request.META.get('HTTP_USER_AGENT', 'unknown')[:100]}"
                    }
                )
                
                messages.success(request, f'¡Bienvenido {username}!')
                return redirect('/login/dashboard/')
            else:
                # Login fallido - registrar intento
                should_block = register_failed_attempt(client_ip, username)
                
                # Obtener contador de intentos
                attempts_key = FAILED_LOGIN_KEY.format(ip=client_ip)
                attempts = cache.get(attempts_key, [])
                attempt_count = len(attempts)
                
                logger.warning(f"❌ LOGIN FALLIDO | Usuario: {username} | IP: {client_ip} | Intentos: {attempt_count}/5")
                
                # Log de seguridad para login fallido
                security_logger.warning(
                    f"Intento de login fallido",
                    extra={
                        'ip': client_ip,
                        'user': username,
                        'event': 'FAILED_LOGIN_ATTEMPT',
                        'details': f"Intentos recientes: {attempt_count}/5 | Contraseña incorrecta"
                    }
                )
                
                # Si alcanzó el límite, log crítico
                if should_block:
                    security_logger.critical(
                        f"POSIBLE ATAQUE DE FUERZA BRUTA DETECTADO",
                        extra={
                            'ip': client_ip,
                            'user': username,
                            'event': 'BRUTE_FORCE_ATTACK_DETECTED',
                            'details': f"IP {client_ip} ha realizado 5 intentos fallidos en 5 minutos. IP bloqueada por 15 minutos."
                        }
                    )
                    messages.error(request, 'Demasiados intentos fallidos. Intente más tarde.')
                else:
                    messages.error(request, f'Usuario o contraseña incorrectos. Intentos restantes: {5 - attempt_count}')
                
                form = CustomLoginForm(request.POST)
                
        except Exception as e:
            logger.critical(f"💥 ERROR EN LOGIN | Usuario: {username} | Error: {str(e)} | IP: {client_ip}")
            logger.critical(traceback.format_exc())
            
            security_logger.error(
                f"Error crítico en login",
                extra={
                    'ip': client_ip,
                    'user': username,
                    'event': 'LOGIN_SYSTEM_ERROR',
                    'details': f"Error: {str(e)[:200]}"
                }
            )
            
            messages.error(request, 'Error en el sistema. Contacte al administrador.')
    
    return render(request, 'login/login.html', {'form': form})


def logout_view(request):
    """Vista de logout con logging de seguridad."""
    client_ip = get_client_ip(request)
    
    if request.user.is_authenticated:
        username = request.user.username
        logger.info(f"🚪 LOGOUT | Usuario: {username} | ID: {request.user.id} | IP: {client_ip}")
        
        security_logger.info(
            f"Logout exitoso",
            extra={
                'ip': client_ip,
                'user': username,
                'event': 'LOGOUT',
                'details': f"Session cerrada"
            }
        )
        
        logout(request)
        messages.info(request, 'Sesión cerrada correctamente')
    else:
        logger.warning(f"Intento de logout sin sesión activa | IP: {client_ip}")
        
        security_logger.warning(
            f"Intento de logout sin sesión",
            extra={
                'ip': client_ip,
                'user': 'Anonymous',
                'event': 'INVALID_LOGOUT_ATTEMPT',
                'details': f"Intento de cerrar sesión sin estar autenticado"
            }
        )
    
    return redirect('/login/')


@login_required
@log_request_metadata
def dashboard_view(request):
    """Dashboard principal con logging de acceso."""
    client_ip = get_client_ip(request)
    
    logger.info(f"Acceso a dashboard | Usuario: {request.user.username} | ID: {request.user.id} | IP: {client_ip}")
    
    # Log de seguridad para acceso a dashboard
    security_logger.info(
        f"Acceso a dashboard",
        extra={
            'ip': client_ip,
            'user': request.user.username,
            'event': 'DASHBOARD_ACCESS',
            'details': f"User ID: {request.user.id}"
        }
    )
    
    context = {
        'user': request.user,
        'username': request.user.username,
    }
    
    return render(request, 'login/dashboard.html', context)