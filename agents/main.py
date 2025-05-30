"""
Módulo principal de selección de agentes.

Este módulo determina qué agente usar basándose en parámetros
desencriptados desde la URL del usuario.
"""

from typing import Optional, Dict, Any, Union
import streamlit as st
from core.security import desencriptar_datos_usuario
from agents.simple_agent import SimpleRRHHAgent


class AgentSelector:
    """
    Clase responsable de seleccionar y crear el agente apropiado
    basándose en los parámetros del usuario.
    """
    
    # Mapeo de tipos de agente disponibles
    AGENT_TYPES = {
        "rrhh": "SimpleRRHHAgent",
        "technical": "TechnicalAgent",  # Para futuro
        "manager": "ManagerAgent",      # Para futuro
        "sales": "SalesAgent",          # Para futuro
        "default": "SimpleRRHHAgent"
    }
    
    # Mapeo de tipos de entrevista
    INTERVIEW_TYPES = {
        "initial": "rrhh",
        "technical": "technical", 
        "final": "manager",
        "sales_demo": "sales",
        "default": "rrhh"
    }
    
    def __init__(self):
        """Inicializa el selector de agentes."""
        self.current_agent = None
        self.user_data = None
    
    def extract_user_data_from_url(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrae y desencripta los datos del usuario desde los parámetros de la URL.
        
        Args:
            query_params: Parámetros de la URL de Streamlit
            
        Returns:
            Diccionario con los datos del usuario desencriptados
        """
        token = query_params.get("token", None)
        
        if token:
            try:
                # Desencriptar datos del usuario
                user_data = desencriptar_datos_usuario(token)
                print(f"📱 Datos usuario desencriptados: {user_data}")
                return user_data
            except Exception as e:
                print(f"❌ Error al desencriptar token: {e}")
                return self._get_fallback_data(query_params)
        else:
            # Fallback: leer parámetros directos de la URL
            return self._get_fallback_data(query_params)
    
    def _get_fallback_data(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtiene datos básicos cuando no hay token o falla la desencriptación.
        
        Args:
            query_params: Parámetros de la URL
            
        Returns:
            Diccionario con datos básicos del usuario
        """
        return {
            "nombre": query_params.get("nombre", "Candidato"),
            "phone": query_params.get("phone"),
            "job-offer": query_params.get("job-offer"),
            "agent_type": query_params.get("agent_type", "default"),
            "interview_type": query_params.get("interview_type", "default"),
            "department": query_params.get("department", "rrhh")
        }
    
    def determine_agent_type(self, user_data: Dict[str, Any]) -> str:
        """
        Determina qué tipo de agente usar basándose en los datos del usuario.
        
        Args:
            user_data: Datos desencriptados del usuario
            
        Returns:
            Tipo de agente a usar
        """
        # Prioridad 1: agent_type explícito
        agent_type = user_data.get("agent_type")
        if agent_type and agent_type in self.AGENT_TYPES:
            print(f"🎯 Agente seleccionado por agent_type: {agent_type}")
            return agent_type
        
        # Prioridad 2: interview_type
        interview_type = user_data.get("interview_type", "default")
        mapped_agent = self.INTERVIEW_TYPES.get(interview_type, "default")
        print(f"🎯 Agente seleccionado por interview_type '{interview_type}': {mapped_agent}")
        return mapped_agent
        
        # Prioridad 3: department
        department = user_data.get("department", "rrhh")
        if department in self.AGENT_TYPES:
            print(f"🎯 Agente seleccionado por department: {department}")
            return department
        
        # Fallback: agente por defecto
        print("🎯 Usando agente por defecto: rrhh")
        return "default"
    
    def create_agent(self, agent_type: str, user_data: Dict[str, Any]):
        """
        Crea una instancia del agente especificado.
        
        Args:
            agent_type: Tipo de agente a crear
            user_data: Datos del usuario para configurar el agente
            
        Returns:
            Instancia del agente configurado
        """
        job_offer_id = user_data.get("job-offer")
        
        # Convertir job_offer_id a string si existe
        if job_offer_id is not None:
            job_offer_id = str(job_offer_id)
        
        if agent_type == "rrhh" or agent_type == "default":
            print(f"🤖 Creando SimpleRRHHAgent para job_offer: {job_offer_id}")
            return SimpleRRHHAgent(id_job_offer=job_offer_id)
        
        elif agent_type == "technical":
            # TODO: Implementar TechnicalAgent en el futuro
            print("⚠️ TechnicalAgent no implementado aún, usando SimpleRRHHAgent")
            return SimpleRRHHAgent(id_job_offer=job_offer_id)
        
        elif agent_type == "manager":
            # TODO: Implementar ManagerAgent en el futuro
            print("⚠️ ManagerAgent no implementado aún, usando SimpleRRHHAgent")
            return SimpleRRHHAgent(id_job_offer=job_offer_id)
        
        elif agent_type == "sales":
            # TODO: Implementar SalesAgent en el futuro
            print("⚠️ SalesAgent no implementado aún, usando SimpleRRHHAgent")
            return SimpleRRHHAgent(id_job_offer=job_offer_id)
        
        else:
            print(f"⚠️ Tipo de agente desconocido '{agent_type}', usando SimpleRRHHAgent")
            return SimpleRRHHAgent(id_job_offer=job_offer_id)
    
    def get_agent_for_user(self, query_params: Dict[str, Any]):
        """
        Método principal que obtiene el agente apropiado para el usuario.
        
        Args:
            query_params: Parámetros de la URL de Streamlit
            
        Returns:
            Tupla (agente, datos_usuario)
        """
        # 1. Extraer datos del usuario
        self.user_data = self.extract_user_data_from_url(query_params)
        
        # 2. Determinar tipo de agente
        agent_type = self.determine_agent_type(self.user_data)
        
        # 3. Crear agente
        self.current_agent = self.create_agent(agent_type, self.user_data)
        
        # 4. Agregar metadatos al agente
        if hasattr(self.current_agent, 'state') and hasattr(self.current_agent.state, 'metadata'):
            self.current_agent.state.metadata.update({
                "agent_type": agent_type,
                "user_data": self.user_data
            })
        
        print(f"✅ Agente configurado exitosamente: {type(self.current_agent).__name__}")
        return self.current_agent, self.user_data


# Función de conveniencia para uso directo
def get_agent_from_url(query_params: Dict[str, Any]):
    """
    Función de conveniencia que retorna el agente apropiado basándose en la URL.
    
    Args:
        query_params: Parámetros de la URL (st.query_params)
        
    Returns:
        Tupla (agente, datos_usuario)
    """
    selector = AgentSelector()
    return selector.get_agent_for_user(query_params)


# Función para obtener información sobre agentes disponibles
def get_available_agents() -> Dict[str, Dict[str, Any]]:
    """
    Retorna información sobre los agentes disponibles.
    
    Returns:
        Diccionario con información de agentes disponibles
    """
    return {
        "rrhh": {
            "name": "Agente de RRHH",
            "description": "Agente para entrevistas iniciales y procesos de recursos humanos",
            "class": "SimpleRRHHAgent",
            "available": True
        },
        "technical": {
            "name": "Agente Técnico", 
            "description": "Agente especializado en entrevistas técnicas de programación",
            "class": "TechnicalAgent",
            "available": False
        },
        "manager": {
            "name": "Agente Gerencial",
            "description": "Agente para entrevistas con management y liderazgo",
            "class": "ManagerAgent", 
            "available": False
        },
        "sales": {
            "name": "Agente de Ventas",
            "description": "Agente especializado en roles de ventas y comerciales",
            "class": "SalesAgent",
            "available": False
        }
    } 