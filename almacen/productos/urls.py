"""
URLs para el módulo de productos.
Incluye tanto vistas web como endpoints de API REST.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router para API REST
router = DefaultRouter()
router.register(r'', views.ProductoViewSet, basename='api-productos')

app_name = 'productos'

urlpatterns = [
    # ===== API REST (v1) =====
    path('api/', include(router.urls)),
    
    # ===== Vistas Web (HTML) =====
    path('', views.lista_productos, name='lista_productos'),
    path('crear/', views.crear_producto, name='crear_producto'),
    path('editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
]