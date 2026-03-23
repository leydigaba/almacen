"""
Vistas para el módulo de productos - UI Web + API REST con logging profesional.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Producto
from .serializers import ProductoSerializer
import logging
import uuid
from datetime import datetime

logger = logging.getLogger('api')


class StandardResultsSetPagination(PageNumberPagination):
    """Paginación estándar para la API."""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductoViewSet(viewsets.ModelViewSet):
    """
    API REST para operaciones CRUD de Productos.
    Endpoints: GET /api/productos/, POST /api/productos/, etc.
    """
    
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    pagination_class = StandardResultsSetPagination
    
    def get_request_id(self):
        """Genera un ID único para rastrear la solicitud."""
        return uuid.uuid4().hex[:8]
    
    def get_user_info(self):
        """Obtiene información del usuario actual."""
        if self.request.user.is_authenticated:
            return self.request.user.username
        return "Anonymous"
    
    def list(self, request, *args, **kwargs):
        """GET /api/productos/ - Obtiene lista de productos."""
        request_id = self.get_request_id()
        user = self.get_user_info()
        
        logger.info(f"[{request_id}] ▶ INICIO GET /api/productos | Usuario: {user}")
        
        try:
            response = super().list(request, *args, **kwargs)
            count = self.queryset.count()
            
            logger.info(f"[{request_id}] ✓ ÉXITO GET /api/productos | "
                       f"Productos encontrados: {count} | Usuario: {user}")
            return response
            
        except Exception as e:
            logger.error(f"[{request_id}] ✗ ERROR GET /api/productos | "
                        f"Error: {str(e)} | Usuario: {user}")
            return Response(
                {'error': 'Error al obtener productos'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def create(self, request, *args, **kwargs):
        """POST /api/productos/ - Crea un nuevo producto."""
        request_id = self.get_request_id()
        user = self.get_user_info()
        
        logger.info(f"[{request_id}] ▶ INICIO POST /api/productos | "
                   f"Datos: nombre={request.data.get('nombre')} | Usuario: {user}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"[{request_id}] ⚠️ VALIDACIÓN FALLIDA POST /api/productos | "
                             f"Errores: {serializer.errors} | Usuario: {user}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_create(serializer)
            logger.info(f"[{request_id}] ✓ ÉXITO POST /api/productos | "
                       f"Producto creado: {serializer.data['nombre']} (ID: {serializer.data['id']}) | Usuario: {user}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"[{request_id}] ✗ ERROR POST /api/productos | "
                        f"Excepción: {str(e)} | Usuario: {user}")
            return Response(
                {'error': 'Error al crear producto'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def retrieve(self, request, *args, **kwargs):
        """GET /api/productos/{id}/ - Obtiene un producto específico."""
        request_id = self.get_request_id()
        user = self.get_user_info()
        producto_id = kwargs.get('pk')
        
        logger.info(f"[{request_id}] ▶ INICIO GET /api/productos/{producto_id}/ | Usuario: {user}")
        
        try:
            response = super().retrieve(request, *args, **kwargs)
            logger.info(f"[{request_id}] ✓ ÉXITO GET /api/productos/{producto_id}/ | "
                       f"Producto: {response.data['nombre']} | Usuario: {user}")
            return response
            
        except Exception as e:
            logger.error(f"[{request_id}] ✗ ERROR GET /api/productos/{producto_id}/ | "
                        f"Error: {str(e)} | Usuario: {user}")
            return Response(
                {'error': 'Producto no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    def update(self, request, *args, **kwargs):
        """PUT /api/productos/{id}/ - Actualiza un producto."""
        request_id = self.get_request_id()
        user = self.get_user_info()
        producto_id = kwargs.get('pk')
        
        logger.info(f"[{request_id}] ▶ INICIO PUT /api/productos/{producto_id}/ | "
                   f"Datos: {request.data} | Usuario: {user}")
        
        try:
            instance = self.get_object()
            nombre_anterior = instance.nombre
            
            serializer = self.get_serializer(instance, data=request.data, partial=False)
            
            if not serializer.is_valid():
                logger.warning(f"[{request_id}] ⚠️ VALIDACIÓN FALLIDA PUT /api/productos/{producto_id}/ | "
                             f"Errores: {serializer.errors} | Usuario: {user}")
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_update(serializer)
            logger.info(f"[{request_id}] ✓ ÉXITO PUT /api/productos/{producto_id}/ | "
                       f"Cambios: {nombre_anterior} → {serializer.data['nombre']} | Usuario: {user}")
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"[{request_id}] ✗ ERROR PUT /api/productos/{producto_id}/ | "
                        f"Excepción: {str(e)} | Usuario: {user}")
            return Response(
                {'error': 'Error al actualizar producto'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def destroy(self, request, *args, **kwargs):
        """DELETE /api/productos/{id}/ - Elimina un producto."""
        request_id = self.get_request_id()
        user = self.get_user_info()
        producto_id = kwargs.get('pk')
        
        try:
            instance = self.get_object()
            nombre_producto = instance.nombre
            
            logger.warning(f"[{request_id}] ⚠️ INICIO DELETE /api/productos/{producto_id}/ | "
                          f"Se eliminará: {nombre_producto} | Usuario: {user}")
            
            self.perform_destroy(instance)
            logger.info(f"[{request_id}] ✓ ÉXITO DELETE /api/productos/{producto_id}/ | "
                       f"Producto eliminado: {nombre_producto} | Usuario: {user}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"[{request_id}] ✗ ERROR DELETE /api/productos/{producto_id}/ | "
                        f"Excepción: {str(e)} | Usuario: {user}")
            return Response(
                {'error': 'Error al eliminar producto'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ==================== VISTAS WEB (HTML) ====================

def lista_productos(request):
    """Vista web: Lista de productos."""
    request_id = uuid.uuid4().hex[:8]
    logger.info(f"[{request_id}] ▶ Acceso a lista web de productos | Usuario: {request.user.username}")
    
    try:
        productos = Producto.objects.all()
        logger.info(f"[{request_id}] ✓ Carga exitosa: {productos.count()} productos")
        return render(request, 'productos/lista.html', {'productos': productos})
    except Exception as e:
        logger.error(f"[{request_id}] ✗ Error cargando lista: {str(e)}")
        return render(request, 'productos/lista.html', {'error': str(e)})


def crear_producto(request):
    """Vista web: Crear producto."""
    request_id = uuid.uuid4().hex[:8]
    logger.info(f"[{request_id}] ▶ Usuario {request.user.username} en formulario crear producto")
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')

        if not nombre:
            logger.warning(f"[{request_id}] ⚠️ Validación fallida: nombre vacío")
            return render(request, 'productos/form.html', {'error': 'Nombre requerido'})

        try:
            Producto.objects.create(nombre=nombre, precio=precio, stock=stock)
            logger.info(f"[{request_id}] ✓ Producto creado: {nombre}")
            return redirect('lista_productos')
        except Exception as e:
            logger.error(f"[{request_id}] ✗ Error creando producto: {str(e)}")
            return render(request, 'productos/form.html', {'error': 'Error al crear'})

    return render(request, 'productos/form.html')


def editar_producto(request, id):
    """Vista web: Editar producto."""
    request_id = uuid.uuid4().hex[:8]
    producto = get_object_or_404(Producto, id=id)
    
    logger.info(f"[{request_id}] ▶ Usuario {request.user.username} editando producto {id}")

    if request.method == 'POST':
        anterior = {
            'nombre': producto.nombre,
            'precio': producto.precio,
            'stock': producto.stock
        }
        
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        producto.save()
        
        logger.info(f"[{request_id}] ✓ Producto actualizado {id}: {anterior} → "
                   f"{{'nombre': {producto.nombre}, 'precio': {producto.precio}, 'stock': {producto.stock}}}")
        return redirect('lista_productos')

    return render(request, 'productos/form.html', {'producto': producto})


def eliminar_producto(request, id):
    """Vista web: Eliminar producto."""
    request_id = uuid.uuid4().hex[:8]
    
    try:
        producto = Producto.objects.get(id=id)
        logger.warning(f"[{request_id}] ⚠️ Usuario {request.user.username} eliminando producto {id}: {producto.nombre}")
        producto.delete()
        logger.info(f"[{request_id}] ✓ Producto {id} eliminado exitosamente")
    except Exception as e:
        logger.error(f"[{request_id}] ✗ Error eliminando producto {id}: {str(e)}")

    return redirect('lista_productos')