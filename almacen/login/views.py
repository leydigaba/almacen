from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .forms import CustomLoginForm
import logging
import traceback
import uuid
from functools import wraps

logger = logging.getLogger('login')

def log_request_metadata(view_func):
    """Decorador para registrar metadatos de la solicitud"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        request.request_id = str(uuid.uuid4())[:8]
        
        logger.info(
            f"[RequestID: {request.request_id}] Inicio de solicitud | "
            f"Método: {request.method} | Ruta: {request.path}"
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
    """Vista de login"""
    # Si ya está autenticado, redirigir al dashboard
    if request.user.is_authenticated:
        logger.info(f"Usuario autenticado {request.user.username} intenta acceder a login | Redirigiendo a dashboard")
        return redirect('/login/dashboard/')  # Usar URL directa
    
    form = CustomLoginForm()
    
    if request.method == 'POST':
        logger.info("=== INICIO OPERACIÓN LOGIN ===")
        username = request.POST.get('username', '')
        
        logger.info(f"Intento de autenticación para usuario: {username}")
        
        try:
            user = authenticate(
                request, 
                username=username, 
                password=request.POST.get('password', '')
            )
            
            if user is not None:
                login(request, user)
                logger.info(f"✅ LOGIN EXITOSO | Usuario: {username} | ID: {user.id} | IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
                messages.success(request, f'¡Bienvenido {username}!')
                return redirect('/login/dashboard/')  # Usar URL directa
            else:
                logger.warning(f"❌ LOGIN FALLIDO | Usuario: {username} | IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
                messages.error(request, 'Usuario o contraseña incorrectos')
                form = CustomLoginForm(request.POST)
                
        except Exception as e:
            logger.critical(f"💥 ERROR EN LOGIN | Usuario: {username} | Error: {str(e)}")
            logger.critical(traceback.format_exc())
            messages.error(request, 'Error en el sistema. Contacte al administrador.')
    
    return render(request, 'login/login.html', {'form': form})

def logout_view(request):
    """Vista de logout"""
    if request.user.is_authenticated:
        username = request.user.username
        logger.info(f"🚪 LOGOUT | Usuario: {username} | ID: {request.user.id} | IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
        logout(request)
        messages.info(request, 'Sesión cerrada correctamente')
    else:
        logger.warning(f"Intento de logout sin sesión activa | IP: {request.META.get('REMOTE_ADDR', 'unknown')}")
    
    return redirect('/login/')  # Usar URL directa

@login_required
@log_request_metadata
def dashboard_view(request):
    """Dashboard principal"""
    logger.info(f"Acceso a dashboard | Usuario: {request.user.username} | ID: {request.user.id}")
    
    context = {
        'user': request.user,
        'username': request.user.username,
    }
    
    return render(request, 'login/dashboard.html', context)