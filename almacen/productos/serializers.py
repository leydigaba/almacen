"""
Serializadores para el módulo de productos.
Convierte modelos Django a JSON y valida datos entrantes.
"""

from rest_framework import serializers
from .models import Producto
import logging

logger = logging.getLogger('api')


class ProductoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Producto."""
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'stock']
        read_only_fields = ['id']
    
    def validate_nombre(self, value):
        """Valida que el nombre no esté vacío."""
        if not value or not value.strip():
            logger.warning(f"⚠️ Validación fallida: nombre vacío")
            raise serializers.ValidationError("El nombre no puede estar vacío")
        
        if len(value) < 3:
            logger.warning(f"⚠️ Validación fallida: nombre muy corto '{value}'")
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        
        return value
    
    def validate_precio(self, value):
        """Valida que el precio sea positivo."""
        if value is None:
            logger.warning(f"⚠️ Validación fallida: precio nulo")
            raise serializers.ValidationError("El precio es requerido")
        
        if value < 0:
            logger.warning(f"⚠️ Validación fallida: precio negativo ({value})")
            raise serializers.ValidationError("El precio no puede ser negativo")
        
        return value
    
    def validate_stock(self, value):
        """Valida que el stock sea no negativo."""
        if value is None:
            logger.warning(f"⚠️ Validación fallida: stock nulo")
            raise serializers.ValidationError("El stock es requerido")
        
        if value < 0:
            logger.warning(f"⚠️ Validación fallida: stock negativo ({value})")
            raise serializers.ValidationError("El stock no puede ser negativo")
        
        return value
    
    def validate(self, data):
        """Validaciones adicionales."""
        logger.debug(f"🔍 Validando producto: {data.get('nombre')}")
        return data
