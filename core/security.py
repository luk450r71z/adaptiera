"""
Funciones de seguridad y criptografía para el proyecto.
"""

import ast
import os
from typing import Dict, Any
from cryptography.fernet import Fernet


def sanitize_input(text: str) -> str:
    """Sanitiza entrada de texto removiendo caracteres potencialmente peligrosos."""
    return text.strip().replace("<", "").replace(">", "")


def get_fernet_key() -> bytes:
    """
    Obtiene la clave Fernet desde variables de entorno.
    
    Returns:
        Clave Fernet en bytes
        
    Raises:
        ValueError: Si FERNET_KEY no está configurada
    """
    key = os.getenv("FERNET_KEY")
    if not key:
        raise ValueError("FERNET_KEY no configurada en variables de entorno")
    return key.encode()


def encriptar_texto(texto: str, clave: bytes = None) -> str:
    """
    Encripta texto usando Fernet.
    
    Args:
        texto: Texto a encriptar
        clave: Clave de encriptación (opcional, usa FERNET_KEY por defecto)
        
    Returns:
        Texto encriptado como string
    """
    if clave is None:
        clave = get_fernet_key()
    
    f = Fernet(clave)
    texto_bytes = texto.encode('utf-8')
    token_encriptado = f.encrypt(texto_bytes)
    return token_encriptado.decode('utf-8')


def desencriptar_texto(texto_encriptado: str, clave: bytes = None) -> str:
    """
    Desencripta texto usando Fernet con múltiples métodos de fallback.
    
    Args:
        texto_encriptado: Texto encriptado a desencriptar
        clave: Clave de encriptación (opcional, usa FERNET_KEY por defecto)
        
    Returns:
        Texto desencriptado
        
    Raises:
        ValueError: Si no se puede desencriptar con ningún método
    """
    if clave is None:
        clave = get_fernet_key()
    
    f = Fernet(clave)
    
    # Métodos a intentar en orden
    methods = [
        # Método 1: ast.literal_eval (para tokens que vienen como "b'...'")
        lambda token: f.decrypt(ast.literal_eval(token)).decode(),
        
        # Método 2: Conversión directa (para tokens Fernet directos)
        lambda token: f.decrypt(token.encode('utf-8')).decode(),
        
        # Método 3: Agregar comilla faltante (código original)
        lambda token: f.decrypt(ast.literal_eval(token + "'")).decode()
    ]
    
    for i, method in enumerate(methods, 1):
        try:
            result = method(texto_encriptado)
            print(f"✅ Método {i} exitoso")
            return result
        except Exception as e:
            print(f"❌ Método {i} falló: {e}")
            continue
    
    # Si todos los métodos fallan
    raise ValueError("No se pudo desencriptar el token con ningún método")


def encriptar_datos_usuario(datos: Dict[str, Any]) -> str:
    """
    Encripta un diccionario de datos de usuario convirtiéndolo a JSON.
    
    Args:
        datos: Diccionario con datos del usuario
        
    Returns:
        Token encriptado como string
    """
    import json
    json_texto = json.dumps(datos, ensure_ascii=False)
    return encriptar_texto(json_texto)


def desencriptar_datos_usuario(token: str) -> Dict[str, Any]:
    """
    Desencripta un token y lo convierte a diccionario de datos de usuario.
    
    Args:
        token: Token encriptado
        
    Returns:
        Diccionario con datos del usuario
    """
    import json
    json_texto = desencriptar_texto(token)
    return json.loads(json_texto)
