import streamlit as st
import sys
import os
import json
from pathlib import Path

# Agregar el directorio raíz al path para las importaciones
sys.path.append(str(Path(__file__).parent.parent.parent))

# Importar configuraciones
from core.rrhh_config import (
    INTERFACE_CONFIG, 
    BUTTONS_CONFIG, 
    HELP_CONFIG, 
    METRICS_CONFIG,
    DOWNLOAD_CONFIG
)

# Importar funciones de seguridad
from core.security import desencriptar_datos_usuario

# Importar agente directamente (simplificado)
from agents.simple_agent import create_simple_rrhh_agent

def lanzar_chatbot():
    """
    Interfaz de Streamlit para el agente conversacional de RRHH
    """
    
    # Leer token cifrado en la URL
    query_params = st.query_params
    token = query_params.get("token", None)

    if token:
        try:
            # Desencriptar directamente a diccionario usando la función modularizada
            datos_usuario = desencriptar_datos_usuario(token)
            print(f"Datos usuario desencriptados: {datos_usuario}")
            
            nombre_usuario = datos_usuario.get("nombre", "Candidato")
            telefono_usuario = datos_usuario.get("phone")
            id_job_offer_raw = datos_usuario.get("job-offer")
            # Convertir id_job_offer a string si existe
            id_job_offer = str(id_job_offer_raw) if id_job_offer_raw is not None else None
        except Exception as e:
            st.error(f"Error al procesar el token: {str(e)}")
            nombre_usuario = "Candidato"
            telefono_usuario = None
            id_job_offer = None
    else:
        # Leer parámetros GET desde la URL
        query_params = st.query_params
        nombre_usuario = query_params.get("nombre", "Candidato")
        telefono_usuario = query_params.get("phone")
        id_job_offer = query_params.get("job-offer")
    
    # Título y descripción usando configuración
    st.subheader(INTERFACE_CONFIG["title"])
    
    # Personalizar mensaje de bienvenida con el nombre del usuario
    if nombre_usuario != "Candidato":
        mensaje_personalizado = f"¡Hola {nombre_usuario}! " + INTERFACE_CONFIG["welcome_message"]
        st.markdown(mensaje_personalizado)
    else:
        st.markdown(INTERFACE_CONFIG["welcome_message"])
    
    # Mostrar información del usuario si está disponible
    if nombre_usuario != "Candidato" or telefono_usuario or id_job_offer:
        with st.expander("👤 Información del candidato"):
            st.write(f"**Nombre:** {nombre_usuario}")
            if telefono_usuario:
                st.write(f"**Teléfono:** {telefono_usuario}")
            if id_job_offer:
                st.write(f"**ID Oferta de Trabajo:** {id_job_offer}")
    
    # Inicializar el agente en session state si no existe
    if "rrhh_agent" not in st.session_state:
        st.session_state.rrhh_agent = create_simple_rrhh_agent(id_job_offer)
        st.session_state.rrhh_conversation_started = False
        st.session_state.rrhh_messages = []
        # Almacenar información del usuario en session state
        st.session_state.nombre_usuario = nombre_usuario
        st.session_state.telefono_usuario = telefono_usuario
        st.session_state.id_job_offer = id_job_offer
    
    # Botón para iniciar/reiniciar la conversación
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button(
            BUTTONS_CONFIG["start"]["text"], 
            type=BUTTONS_CONFIG["start"]["type"]
        ):
            # Reiniciar el agente
            job_offer_id = st.session_state.get("id_job_offer")
            st.session_state.rrhh_agent = create_simple_rrhh_agent(job_offer_id)
            st.session_state.rrhh_conversation_started = True
            st.session_state.rrhh_messages = []
            
            # Obtener mensaje inicial
            initial_message = st.session_state.rrhh_agent.start_conversation()
            st.session_state.rrhh_messages.append({
                "role": "assistant", 
                "content": initial_message
            })
            st.rerun()
    
    with col2:
        if st.button(
            BUTTONS_CONFIG["restart"]["text"], 
            type=BUTTONS_CONFIG["restart"]["type"]
        ):
            job_offer_id = st.session_state.get("id_job_offer")
            st.session_state.rrhh_agent = create_simple_rrhh_agent(job_offer_id)
            st.session_state.rrhh_conversation_started = False
            st.session_state.rrhh_messages = []
            st.rerun()
    
    with col3:
        if st.session_state.get("rrhh_conversation_started", False):
            # Mostrar progreso usando configuración
            summary = st.session_state.rrhh_agent.get_conversation_summary()
            progress = summary.get('questions_asked', 0) / max(summary.get('total_questions', 1), 1)
            st.metric(
                METRICS_CONFIG["progress_label"], 
                f"{summary.get('questions_asked', 0)}/{summary.get('total_questions', 0)}", 
                f"{int(progress * 100)}%"
            )
    
    # Mostrar el historial de mensajes si la conversación ha comenzado
    if st.session_state.get("rrhh_conversation_started", False):
        st.markdown("---")
        st.markdown("### 💬 Conversación")
        
        # Mostrar mensajes usando contenedores nativos de Streamlit
        for i, message in enumerate(st.session_state.rrhh_messages):
            if message["role"] == "user":
                # Mensaje del usuario - usando columnas para alineación
                col1, col2 = st.columns([1, 4])
                with col2:
                    st.info(f"**👤 Tú:** {message['content']}")
            else:
                # Mensaje del asistente
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.success(f"**🤖 Agente RRHH:** {message['content']}")
        
        # Verificar si la conversación está completa
        if st.session_state.rrhh_agent.is_conversation_complete():
            st.balloons()
            st.success(INTERFACE_CONFIG["completion_message"])
            
            # Mostrar resumen final
            with st.expander("📊 Ver resumen de la entrevista"):
                summary = st.session_state.rrhh_agent.get_conversation_summary()
                
                st.write("**Respuestas proporcionadas:**")
                for question, answer in summary.get('responses', {}).items():
                    st.write(f"**P:** {question}")
                    st.write(f"**R:** {answer}")
                    st.write("---")
                
                st.write(f"**Total de preguntas respondidas:** {summary.get('questions_asked', 0)}")
                st.write(f"**Total de mensajes intercambiados:** {summary.get('messages_count', 0)}")
            
            # Botón para descargar resumen usando configuración
            if st.button(BUTTONS_CONFIG["download"]["text"]):
                summary = st.session_state.rrhh_agent.get_conversation_summary()
                
                # Crear contenido del archivo usando configuración
                content = f"{DOWNLOAD_CONFIG['header']}\n"
                content += f"{DOWNLOAD_CONFIG['separator']}\n\n"
                
                for question, answer in summary.get('responses', {}).items():
                    content += f"PREGUNTA: {question}\n"
                    content += f"RESPUESTA: {answer}\n\n"
                
                content += f"Preguntas respondidas: {summary.get('questions_asked', 0)}\n"
                content += f"Total de mensajes: {summary.get('messages_count', 0)}\n"
                
                st.download_button(
                    label="💾 Descargar como TXT",
                    data=content,
                    file_name=DOWNLOAD_CONFIG["filename"],
                    mime=DOWNLOAD_CONFIG["mime_type"]
                )
        
        else:
            # Campo para nueva respuesta usando text_area
            st.markdown("### ✍️ Tu respuesta:")
            user_input = st.text_area(
                "Escribe tu respuesta aquí:",
                height=100,
                placeholder="Escribe tu respuesta de manera clara y detallada..."
            )
            
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                if st.button("📤 Enviar Respuesta", type="primary"):
                    if user_input.strip():
                        # Agregar mensaje del usuario al historial
                        st.session_state.rrhh_messages.append({
                            "role": "user", 
                            "content": user_input
                        })
                        
                        # Procesar respuesta con el agente
                        try:
                            with st.spinner("🤔 Procesando tu respuesta..."):
                                agent_response = st.session_state.rrhh_agent.process_user_input(user_input)
                            
                            # Agregar respuesta del agente al historial
                            st.session_state.rrhh_messages.append({
                                "role": "assistant", 
                                "content": agent_response
                            })
                            
                            st.rerun()
                            
                        except ValueError as ve:
                            # Error de configuración (ej: GROQ_API_KEY faltante)
                            st.error("🔧 **Error de Configuración**")
                            st.error(str(ve))
                            st.warning("⚠️ **Acción requerida:** Contacta al administrador del sistema para configurar las credenciales necesarias.")
                            
                        except RuntimeError as re:
                            # Error de Groq (ej: problemas de conexión, API)
                            st.error("🌐 **Error de Conexión con IA**")
                            with st.expander("Ver detalles del error"):
                                st.error(str(re))
                            st.warning("🔄 **Sugerencia:** Intenta enviar tu respuesta nuevamente en unos segundos.")
                            
                        except Exception as e:
                            # Otros errores inesperados
                            st.error("❌ **Error Inesperado**")
                            st.error(f"Tipo: {type(e).__name__}")
                            st.error(f"Detalles: {str(e)}")
                            st.warning("🔄 **Opciones:**")
                            st.warning("1. Intenta enviar tu respuesta nuevamente")
                            st.warning("2. Usa el botón 'Reiniciar' para comenzar de nuevo")
                            st.warning("3. Contacta al soporte técnico si el problema persiste")
                    else:
                        st.warning("Por favor, escribe una respuesta antes de enviar.")
    
    else:
        # Mostrar información inicial
        st.info("👆 Haz clic en 'Iniciar Entrevista' para comenzar la conversación con nuestro agente de RRHH.")
        
        # Mostrar información sobre el proceso usando configuración
        with st.expander(HELP_CONFIG["info_title"]):
            st.markdown(HELP_CONFIG["expectations"])
            st.markdown(HELP_CONFIG["tips"])



if __name__ == "__main__":
    # Configuración de la página para deployment independiente
    st.set_page_config(
        page_title="Adaptiera - Chatbot RRHH",
        page_icon="🤖",
        layout="wide"
    )
    
    # Ejecutar el chatbot directamente
    lanzar_chatbot() 