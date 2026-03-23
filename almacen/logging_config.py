"""
Configuración centralizada de logging para la aplicación Almacén.
Implementa buenas prácticas para logs profesionales.
"""

import logging
import logging.config
from pathlib import Path
from datetime import datetime

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# Crear directorio de audit logs
AUDIT_DIR = LOG_DIR / 'audit'
AUDIT_DIR.mkdir(exist_ok=True)


class ColoredFormatter(logging.Formatter):
    """Formateador con colores para consola."""
    
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[92m',       # Green
        'WARNING': '\033[93m',    # Yellow
        'ERROR': '\033[91m',      # Red
        'CRITICAL': '\033[95m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.COLORS['DEBUG'])
        record.levelname = f"{log_color}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    
    'formatters': {
        'simple': {
            'format': '[%(levelname)s] %(asctime)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'detailed': {
            'format': '[%(levelname)s] %(asctime)s | %(name)s.%(funcName)s:%(lineno)d | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'colored': {
            '()': ColoredFormatter,
            'format': '[%(levelname)s] %(asctime)s | %(name)s | %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
        'audit': {
            'format': '%(asctime)s | USUARIO: %(user)s | ACCIÓN: %(action)s | DETALLES: %(details)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    
    'handlers': {
        # Consola con colores
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'colored',
            'stream': 'ext://sys.stdout',
        },
        
        # Archivo general
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'app.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'level': 'DEBUG',
            'formatter': 'detailed',
        },
        
        # Archivo de errores
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'errors.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'level': 'ERROR',
            'formatter': 'detailed',
        },
        
        # Archivo de auditoría (operaciones sensibles)
        'audit_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(AUDIT_DIR / 'audit.log'),
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'level': 'INFO',
            'formatter': 'detailed',
        },
    },
    
    'loggers': {
        # Logger para módulo de productos
        'productos': {
            'handlers': ['console', 'file', 'error_file', 'audit_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # Logger para módulo de login
        'login': {
            'handlers': ['console', 'file', 'error_file', 'audit_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # Logger de API REST
        'api': {
            'handlers': ['console', 'file', 'error_file', 'audit_file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        
        # Logger de Django (menos verbose)
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
    
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}


def setup_logging():
    """Inicializa la configuración de logging."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger('api')
    logger.info("=" * 60)
    logger.info("🚀 Sistema de logging inicializado correctamente")
    logger.info(f"📁 Directorio de logs: {LOG_DIR}")
    logger.info("=" * 60)
    return logger
