"""
Script para probar la seguridad del módulo de login.
Ejecutar con: python test_security.py
"""

import requests
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/login/"

def test_brute_force():
    """Simula un ataque de fuerza bruta."""
    print(f"\n{'='*60}")
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Iniciando prueba de fuerza bruta...")
    print(f"{'='*60}")
    
    passwords = ['123456', 'password', 'admin123', 'test', 'wrongpass', 'incorrect']
    
    for i, pwd in enumerate(passwords, 1):
        print(f"Intento {i}/6: admin / {pwd}")
        
        response = requests.post(LOGIN_URL, data={
            'username': 'admin',
            'password': pwd
        })
        
        print(f"  → Status: {response.status_code}")
        
        if "Demasiados intentos" in response.text:
            print(f"  ⚠️  ¡IP bloqueada después de {i} intentos!")
            break
        
        time.sleep(1)  # Pequeña pausa entre intentos
    
    print(f"\n{'='*60}")

def test_sql_injection():
    """Prueba inyección SQL en login."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Probando inyección SQL...")
    
    payloads = [
        ("' OR '1'='1", "anything"),
        ("admin'--", "anything"),
        ("'; DROP TABLE users; --", "anything"),
    ]
    
    for username, password in payloads:
        print(f"Probando: username='{username}'")
        response = requests.post(LOGIN_URL, data={
            'username': username,
            'password': password
        })
        print(f"  → Status: {response.status_code}")

def test_xss():
    """Prueba XSS en login."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Probando XSS...")
    
    xss_payload = "<script>alert('XSS')</script>"
    response = requests.post(LOGIN_URL, data={
        'username': xss_payload,
        'password': 'test'
    })
    print(f"Payload XSS: {xss_payload}")
    print(f"  → Status: {response.status_code}")

def test_unauthorized_access():
    """Prueba acceso no autorizado."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Probando acceso no autorizado...")
    
    urls = [
        '/login/dashboard/',
        '/productos/',
        '/admin/',
    ]
    
    for url in urls:
        response = requests.get(f"{BASE_URL}{url}")
        print(f"Accediendo a {url} → Status: {response.status_code}")

if __name__ == "__main__":
    print("\n🔒 INICIANDO PRUEBAS DE SEGURIDAD DEL MÓDULO LOGIN 🔒")
    
    test_unauthorized_access()
    test_xss()
    test_sql_injection()
    test_brute_force()
    
    print("\n✅ Pruebas completadas. Revisar logs/security/security.log")