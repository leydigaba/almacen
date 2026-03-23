from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto
import logging

logger = logging.getLogger(__name__)

# LISTAR
def lista_productos(request):
    logger.info("Acceso a lista de productos")
    productos = Producto.objects.all()
    return render(request, 'productos/lista.html', {'productos': productos})

# CREAR
def crear_producto(request):
    logger.info(f"{request.user.username} inició creación de producto")
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')

        if not nombre:
            logger.warning(f"{request.user.username} intentó crear producto sin nombre")
            return render(request, 'productos/form.html', {'error': 'Nombre requerido'})

        try:
            Producto.objects.create(nombre=nombre, precio=precio, stock=stock)
            logger.info(f"Producto creado por {request.user.username}: {nombre}")
            return redirect('lista_productos')
        except Exception as e:
            logger.error(f"Error al crear producto por {request.user.username}: {str(e)}")
            return render(request, 'productos/form.html', {'error': 'Error al crear producto'})
    return render(request, 'productos/form.html')

# EDITAR
def editar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    logger.info(f"{request.user.username} editando producto ID {id}")

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        producto.save()
        logger.info(f"Producto actualizado ID {id} por {request.user.username}")
        return redirect('lista_productos')

    return render(request, 'productos/form.html', {'producto': producto})

# ELIMINAR
def eliminar_producto(request, id):
    try:
        producto = Producto.objects.get(id=id)
        logger.warning(f"{request.user.username} eliminando producto ID {id}")
        producto.delete()
        logger.info(f"Producto eliminado ID {id} por {request.user.username}")
    except Exception as e:
        logger.error(f"Error eliminando producto ID {id} por {request.user.username}: {str(e)}")
    return redirect('lista_productos')