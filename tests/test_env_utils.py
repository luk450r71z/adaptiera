#!/usr/bin/env python3
"""
Script de prueba para las utilidades de entorno.
"""

from utils.env_utils import (
    load_env_variables,
    get_env_variable,
    check_required_env_variables,
    print_env_status
)

def main():
    print("🧪 Probando utilidades de entorno...")
    print("=" * 50)
    
    # 1. Cargar variables de entorno
    print("\n1. Cargando variables de entorno:")
    success = load_env_variables()
    print(f"   Carga exitosa: {success}")
    
    # 2. Obtener variable específica
    print("\n2. Obteniendo variables específicas:")
    groq_key = get_env_variable("GROQ_API_KEY", default="No configurada")
    print(f"   GROQ_API_KEY: {'Configurada' if groq_key != 'No configurada' else 'No configurada'}")
    
    # 3. Verificar variables requeridas
    print("\n3. Verificando variables requeridas:")
    required = ["GROQ_API_KEY", "SMTP_SERVER"]
    missing = check_required_env_variables(required)
    
    if missing:
        print(f"   ⚠️  Variables faltantes: {missing}")
    else:
        print(f"   ✅ Todas las variables requeridas están presentes")
    
    # 4. Mostrar estado general
    print("\n4. Estado general de variables:")
    print_env_status()
    
    print("\n🎉 Prueba completada!")

if __name__ == "__main__":
    main() 