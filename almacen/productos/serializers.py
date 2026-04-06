"""
Serializadores para el módulo de productos.
Convierte modelos Django a JSON y valida datos entrantes.
"""

from rest_framework import serializers
from .models import Producto
import logging
import re

logger = logging.getLogger('api')
security_logger = logging.getLogger('security')


class ProductoSerializer(serializers.ModelSerializer):
    """Serializador para el modelo Producto."""
    
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'stock']
        read_only_fields = ['id']
    
    def _detect_malicious_payload(self, value, field_name):
        """Detecta patrones maliciosos: inyecciones SQL, scripts, etc."""
        if not isinstance(value, str):
            return False
        
        malicious_patterns = [
            r"(?i)(drop|delete|insert|update|select|union|exec|execute|script|onload|onerror|<.*>|javascript:|alert\()",
            r"(?i)(-{2}|;|--|/\*|\*\/|xp_|sp_)",  # SQL comments/stored procs
            r"(?i)(<script|<iframe|<!doctype|<svg|<img|<object|<embed|<video)",  # HTML/JavaScript
        ]
        
        for pattern in malicious_patterns:
            if re.search(pattern, value):
                security_logger.critical(
                    f"🚨 PAYLOAD MALICIOSO DETECTADO | Field: {field_name} | "
                    f"Valor: {value[:100]} | Patrón: {pattern}"
                )
                return True
        
        return False
    
    def validate_nombre(self, value):
        """Valida que el nombre no esté vacío ni contenga código malicioso."""
        if not value or not value.strip():
            logger.warning(f"⚠️ Validación fallida: nombre vacío")
            raise serializers.ValidationError("El nombre no puede estar vacío")
        
        if len(value) < 3:
            logger.warning(f"⚠️ Validación fallida: nombre muy corto '{value}'")
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        
        # Detección de payloads maliciosos
        if self._detect_malicious_payload(value, 'nombre'):
            raise serializers.ValidationError("El nombre contiene caracteres maliciosos")
        
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
