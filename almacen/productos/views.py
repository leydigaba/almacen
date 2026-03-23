from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
import logging
import uuid

logger = logging.getLogger(__name__)

# ------------------------------
# LISTAR PRODUCTOS
# ------------------------------
def lista_productos(request):
    request_id = uuid.uuid4().hex[:8]
    logger.info(f"[RequestID: {request_id}] Inicio de solicitud | Método: {request.method} | Ruta: {request.path}")
    
    productos = Producto.objects.all()
    logger.info(f"[RequestID: {request_id}] Acceso a lista de productos | Usuario: {request.user.username}")
    
    response = render(request, 'productos/lista.html', {'productos': productos})
    logger.info(f"[RequestID: {request_id}] Solicitud completada | Status: {response.status_code}")
    return response

# ------------------------------
# CREAR PRODUCTO
# ------------------------------
def crear_producto(request):
    request_id = uuid.uuid4().hex[:8]
    logger.info(f"[RequestID: {request_id}] Inicio de solicitud | Método: {request.method} | Ruta: {request.path}")
    logger.info(f"[RequestID: {request_id}] Usuario {request.user.username} inició creación de producto")
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')

        if not nombre:
            logger.warning(f"[RequestID: {request_id}] {request.user.username} intentó crear producto sin nombre")
            response = render(request, 'productos/form.html', {'error': 'Nombre requerido'})
            logger.info(f"[RequestID: {request_id}] Solicitud completada | Status: {response.status_code}")
            return response

        try:
            Producto.objects.create(nombre=nombre, precio=precio, stock=stock)
            logger.info(f"[RequestID: {request_id}] Producto creado por {request.user.username}: {nombre}")
            response = redirect('lista_productos')
            logger.info(f"[RequestID: {request_id}] Solicitud completada | Status: {response.status_code}")
            return response
        except Exception as e:
            logger.error(f"[RequestID: {request_id}] Error al crear producto por {request.user.username}: {str(e)}")
            response = render(request, 'productos/form.html', {'error': 'Error al crear producto'})
            logger.info(f"[RequestID: {request_id}] Solicitud completada | Status: {response.status_code}")
            return response

    response = render(request, 'productos/form.html')
    logger.info(f"[RequestID: {request_id}] Solicitud completada | Status: {response.status_code}")
    return response

# ------------------------------
# EDITAR PRODUCTO
# ------------------------------
def editar_producto(request, id):
    request_id = uuid.uuid4().hex[:8]
    producto = get_object_or_404(Producto, id=id)
    logger.info(f"[RequestID: {request_id}] Usuario {request.user.username} editando producto ID {id}")

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        producto.save()
        logger.info(f"[RequestID: {request_id}] Producto actualizado ID {id} por {request.user.username}")
        response = redirect('lista_productos')
        logger.info(f"[RequestID: {request_id}] Solicitud completada | Status: {response.status_code}")
        return response

    response = render(request, 'productos/form.html', {'producto': producto})
    logger.info(f"[RequestID: {request_id}] Solicitud completada | Status: {response.status_code}")
    return response

# ------------------------------
# ELIMINAR PRODUCTO
# ------------------------------
def eliminar_producto(request, id):
    request_id = uuid.uuid4().hex[:8]
    try:
        producto = Producto.objects.get(id=id)
        logger.warning(f"[RequestID: {request_id}] Usuario {request.user.username} eliminando producto ID {id}")
        producto.delete()
        logger.info(f"[RequestID: {request_id}] Producto eliminado ID {id} por {request.user.username}")
    except Exception as e:
        logger.error(f"[RequestID: {request_id}] Error eliminando producto ID {id} por {request.user.username}: {str(e)}")

    response = redirect('lista_productos')
    logger.info(f"[RequestID: {request_id}] Solicitud completada | Status: {response.status_code}")
    return response