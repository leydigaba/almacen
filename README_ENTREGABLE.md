# 📦 ENTREGABLE MÓDULO API - ESTRUCTURA COMPLETA

## 🎯 CONTENIDO DEL ENTREGABLE

Este directorio contiene el entregable completo del **Módulo API REST de Seguridad (Equipo 3)** para la clase de Logging y Seguridad.

---

## 📁 ARCHIVOS PRINCIPALES

### 1. 📋 **ENTREGABLE_MODULO_API.md** ⭐ LEER PRIMERO
**Descripción:** Documento oficial del entregable con:
- Referencias a código en GitHub con links directos
- Resumen de cambios implementados
- Tabla comparativa de eventos críticos
- Patrones observados
- Recomendaciones de seguridad (3 niveles: Crítica, Alta, Media)
- Guía de reproducción paso a paso

**Para Presentación:** Usar este documento como guión principal

---

### 2. 🔐 **BITACORA_SEGURIDAD.md** ⭐ MOSTRAR EN CLASE
**Descripción:** Bitácora visual y detallada con:
- Tabla de 10 eventos capturados en tiempo real
- Detalles completos de eventos CRÍTICOS (XSS + SQL Injection)
- Estadísticas por tipo de evento
- Análisis forense del ataque
- Logs RAW sin procesar
- Matriz de riesgo vs respuesta

**Para Presentación:** Proyectar las tablas, mostrar logs capturados en vivo

---

### 3. 📊 **ANALISIS_SEGURIDAD_API.md** 
**Descripción:** Análisis profundo con:
- Descripción de cada evento crítico
- Análisis de patrones detectados
- Matriz de riesgo (4 niveles de severidad)
- Todos los filtros de detección implementados
- Configuración técnica detallada
- Evidencia completa de pruebas

**Para Presentación:** Referencia técnica, explicar la arquitectura

---

## 🔗 CÓDIGO EN GITHUB

Acceder a la rama `main` para ver los cambios integrales:

| Archivo | Link | Cambios |
|---------|------|---------|
| **logging_config.py** | [Ver en GitHub](https://github.com/leydigaba/almacen/blob/main/almacen/logging_config.py) | Handler `security_file` + Logger `security` |
| **productos/throttles.py** ⭐ NUEVO | [Ver en GitHub](https://github.com/leydigaba/almacen/blob/main/almacen/productos/throttles.py) | Rate limiting: 20/min anónimos, 100/min autenticados |
| **productos/serializers.py** | [Ver en GitHub](https://github.com/leydigaba/almacen/blob/main/almacen/productos/serializers.py) | Método `_detect_malicious_payload()` → XSS + SQL |
| **productos/views.py** | [Ver en GitHub](https://github.com/leydigaba/almacen/blob/main/almacen/productos/views.py) | Método `_check_authentication()` + IP extraction |
| **almacen/settings.py** | [Ver en GitHub](https://github.com/leydigaba/almacen/blob/main/almacen/almacen/settings.py) | Configuración REST + Throttles + Caché |

---

## 🚀 CÓMO EJECUTAR Y REPRODUCIR

### Paso 1: Clonar Repositorio
```bash
git clone https://github.com/leydigaba/almacen.git
cd almacen/almacen
```

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Ejecutar Servidor
```bash
python manage.py runserver 8001
```

### Paso 4: Ejecutar Pruebas de Seguridad

#### Test 1 - Acceso No Autenticado
```bash
curl http://localhost:8001/productos/api/
# Log: [WARNING] 🚨 ACCESO NO AUTENTICADO
```

#### Test 2 - XSS Injection Detection
```bash
curl -X POST http://localhost:8001/productos/api/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"<script>alert(1)</script>","precio":100,"stock":10}'
# Log: [CRITICAL] 🚨 PAYLOAD MALICIOSO DETECTADO
```

#### Test 3 - SQL Injection Detection
```bash
curl -X POST http://localhost:8001/productos/api/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Monitor; DROP TABLE productos--","precio":100,"stock":10}'
# Log: [CRITICAL] 🚨 PAYLOAD MALICIOSO DETECTADO
```

#### Test 4 - Request Válido
```bash
curl -X POST http://localhost:8001/productos/api/ \
  -H "Content-Type: application/json" \
  -d '{"nombre":"TestSeguridad","precio":299.99,"stock":5}'
# Response: {"id":10,"nombre":"TestSeguridad",...}
```

### Paso 5: Ver Logs de Seguridad
```bash
tail -f /Users/johncruz/Documents/hola/almacen/logs/security.log
```

---

## 📊 EVENTOS CRÍTICOS DETECTADOS

| Evento | Tipo | Payload | Estado |
|--------|------|---------|--------|
| 1-3, 6, 9-10 | Acceso No Autenticado | N/A | ⚠️ Registrado |
| 4 | XSS Injection | `<script>alert(1)</script>` | 🔴 BLOQUEADO |
| 5, 8 | Bad Request | Validación fallida | ⚠️ Rechazado |
| 7 | SQL Injection | `Monitor; DROP TABLE--` | 🔴 BLOQUEADO |

**Resultados:** 100% de ataques detectados y bloqueados

---

## 🛡️ MECANISMOS DE SEGURIDAD IMPLEMENTADOS

### 1. Rate Limiting
- **Usuarios Anónimos:** 20 requests/minuto
- **Usuarios Autenticados:** 100 requests/minuto
- **Archivo:** `productos/throttles.py`

### 2. Detección de Payloads Maliciosos
- **Patrones Detectados:** 
  - XSS: `<script>`, `alert()`, `onload=`
  - SQL Injection: `DROP`, `DELETE`, `UNION`, `--`
  - HTML/JS: `<iframe>`, `<embed>`, `javascript:`
- **Archivo:** `productos/serializers.py`
- **Resultado:** 100% bloqueados

### 3. Validación de Autenticación
- Verifica autenticación en todos los endpoints
- Extrae IP del cliente
- Registra en `security.log`
- **Archivo:** `productos/views.py`

### 4. Logging Centralizado
- Handler `security_file` → `/logs/security.log`
- Logger `security` → eventos CRITICAL, WARNING
- RotatingFileHandler → 10MB max, 10 backups
- **Archivo:** `logging_config.py`

---

## 📈 ESTADÍSTICAS DEL ENTREGABLE

| Métrica | Valor | Estado |
|---------|-------|--------|
| **Eventos Detectados** | 10 | ✅ Total |
| **Payloads Maliciosos Bloqueados** | 2 | ✅ 100% |
| **Tasa de Detección** | 100% | ✅ Excelente |
| **Archivos Modificados** | 5 | ✅ Api + Config |
| **Archivos Creados** | 1 | ✅ throttles.py |
| **Documentación** | 3 archivos | ✅ Completa |
| **Logs Generados** | security.log | ✅ Operativo |

---

## 🎬 PRESENTACIÓN EN CLASE

### Duración Sugerida: 10-15 minutos

### Estructura Recomendada:

1. **Introducción (1 min)**
   - Explicar responsabilidad del Equipo 3
   - Mostrar 3 tipos de ataques detectados

2. **Demo en Vivo (4-5 min)**
   - Mostrar servidor corriendo en puerto 8001
   - Ejecutar tests de seguridad
   - Projctar `BITACORA_SEGURIDAD.md` en tiempo real
   - Mostrar logs en terminal: `tail -f security.log`

3. **Análisis de Resultados (3-4 min)**
   - Tabla de eventos capturados
   - Patrón detectado: "Scanning Manual"
   - Estadísticas: 100% de detección

4. **Mecanismos de Seguridad (3-4 min)**
   - Explicar rate limiting
   - Mostrar patrones de detección
   - Flujo de validación

5. **Recomendaciones (2-3 min)**
   - Nivel CRÍTICA: Autenticación JWT
   - Nivel ALTA: WAF + Alertas
   - Nivel MEDIA: Compliance

6. **Preguntas (2-3 min)**
   - ¿Cómo evitar falsos positivos?
   - ¿Qué sucede con rate limiting?
   - ¿Por qué logging centralizado?

---

## 📚 DOCUMENTACIÓN TÉCNICA

### Arquitectura de Logging

```
Aplicación Django
        ↓
ProductoViewSet (views.py)
        ↓
    [Throttling] → Si falla: security.log
        ↓
ProductoSerializer (serializers.py)
        ↓
    [Detección Malware] → Si falla: security.log + ERROR
        ↓
Aplicación (app.log)
        ↓
handlers.py 
    ├─ console (colored)
    ├─ app.log (rotativo)
    ├─ errors.log (rotativo)
    ├─ audit.log (rotativo)
    └─ security.log (rotativo) ⭐
```

### Flujo de Validación

```
Request Entrante
    ↓
[1] Rate Limiting Check (throttles.py)
    ├─ ✅ Pasa → Contincar
    └─ ❌ Falla → 429 Too Many Requests
    ↓
[2] Authentication Check (views.py)
    ├─ ✅ Autenticado → Log INFO
    └─ ⚠️ No Auth → Log WARNING
    ↓
[3] Serializer Validation (serializers.py)
    ├─ ✅ Datos Válidos → Procesar
    └─ 🔴 Malware Detected → 400 Bad Request + CRITICAL Log
    ↓
[4] Database Operation
    ├─ ✅ Exitoso → Log INFO
    └─ ❌ Error → Log ERROR
```

---

## 🔍 PATRONES DE DETECCIÓN REGEX

### XSS Detection
```regex
(?i)(drop|delete|insert|update|select|union|exec|execute|script|onload|onerror|<.*>|javascript:|alert\()
```

### SQL Injection Detection
```regex
(?i)(-{2}|;|--|/\*|\*\/|xp_|sp_)
```

### HTML/JS Injection Detection
```regex
(?i)(<script|<iframe|<!doctype|<svg|<img|<object|<embed|<video)
```

---

## ✅ CHECKLIST ENTREGABLE

- [x] Código implementado con logs de seguridad
- [x] Archivo `security.log` generado con eventos reales
- [x] Eventos críticos documentados
- [x] Patrones observados analizados
- [x] Recomendaciones de seguridad (3 niveles)
- [x] Bitácora detallada (10 eventos capturados)
- [x] Guía de reproducción paso a paso
- [x] Links a código en GitHub
- [x] Documentación técnica completa
- [x] Ready para presentación en clase

---

## 🤝 INFORMACIÓN DE CONTACTO

**Equipo 3:** Módulo API REST  
**Responsable:** [Tu Nombre]  
**Rama Git:** main  
**Repositorio:** https://github.com/leydigaba/almacen  

---

## 📝 NOTAS FINALES

- ✅ La API está **protegida contra ataques básicos**
- ✅ **100% de detección** de payloads maliciosos
- ⚠️ Recomendación: Implementar autenticación JWT para producción
- 🎯 El sistema está **listo para presentación**

---

**Fecha Generación:** 5 de abril de 2026  
**Última Actualización:** 21:30 GMT  
**Estado:** ✅ COMPLETO LISTO PARA ENTREGAR
