#!/usr/bin/env python3
"""
Test básico del agente de RRHH simplificado.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from agents.simple_agent import create_simple_rrhh_agent

def test_agent_basic():
    """Prueba básica del agente"""
    print("🧪 Iniciando prueba básica del agente...")
    
    # Crear agente
    agent = create_simple_rrhh_agent()
    
    # Iniciar conversación
    print("\n1. Iniciando conversación...")
    response = agent.start_conversation()
    print(f"Agente: {response}")
    
    # Simular respuestas del usuario
    responses = [
        "Juan Pérez",
        "Tengo 3 años de experiencia como desarrollador",
        "Python, JavaScript, React"
    ]
    
    for i, user_input in enumerate(responses, 2):
        if not agent.is_conversation_complete():
            print(f"\n{i}. Usuario: {user_input}")
            response = agent.process_user_input(user_input)
            print(f"Agente: {response}")
        else:
            break
    
    # Mostrar resumen
    print("\n📊 Resumen final:")
    summary = agent.get_conversation_summary()
    print(f"Respuestas: {summary['questions_asked']}/{summary['total_questions']}")
    print(f"Conversación completa: {summary['complete']}")
    
    return True

def test_agent_with_vacancy():
    """Prueba el agente con una vacante específica"""
    print("\n🧪 Iniciando prueba con vacante específica...")
    
    # Crear agente con vacante específica
    agent = create_simple_rrhh_agent("dev_frontend")
    
    # Iniciar conversación
    print("\n1. Iniciando conversación para dev_frontend...")
    response = agent.start_conversation()
    print(f"Agente: {response[:100]}...")
    
    # Verificar que cargó las preguntas específicas
    summary = agent.get_conversation_summary()
    print(f"Total de preguntas cargadas: {summary['total_questions']}")
    
    return True

def main():
    """Función principal"""
    print("=" * 50)
    print("PRUEBAS DEL AGENTE SIMPLE DE RRHH")
    print("=" * 50)
    
    tests = [
        ("Prueba básica", test_agent_basic),
        ("Prueba con vacante", test_agent_with_vacancy)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            print(f"\n{name}:")
            result = test_func()
            results.append((name, result))
            print(f"✅ {name} completada")
        except Exception as e:
            print(f"❌ {name} falló: {e}")
            results.append((name, False))
    
    # Resumen final
    print("\n" + "=" * 50)
    print("RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{name}: {status}")

if __name__ == "__main__":
    main() 