import streamlit as st
import sys
import os
# Añadir el directorio actual al path para los imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from views.chatbot import lanzar_chatbot
from views.form_candidate_contact import mostrar_formulario as mostrar_formulario_candidatos

# Configuración de la página
st.set_page_config(
    page_title="Adaptiera - Portal Principal",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("Adaptiera - Portal Principal")
st.markdown("### Plataforma de reclutamiento y atención al candidato")

# Menú en la barra lateral
st.sidebar.title("Menú")
opciones = ["Seleccione una opción...", "Formulario de Contacto de Candidato", "Chatbot"]
opcion = st.sidebar.selectbox("", opciones)

# Mostrar el contenido según la opción seleccionada
if opcion == "Seleccione una opción..." or opcion is None:
    # Pantalla de bienvenida
    st.image("https://via.placeholder.com/800x300?text=Adaptiera", use_container_width=True)
    
    st.header("Bienvenido a Adaptiera")
    st.markdown("""
    ### Plataforma integral de reclutamiento y selección
    
    Selecciona una opción del menú lateral para comenzar:
    
    - **Formulario de Contacto de Candidato**: Invita a candidatos a participar en procesos de selección.
    - **Chatbot**: Interactúa con nuestro asistente virtual para resolver dudas.
    """)
    
    # Crear dos columnas para mostrar características
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Reclutamiento eficiente")
        st.markdown("""
        - Automatiza el proceso de contacto
        - Mantén un seguimiento efectivo
        - Mejora la experiencia del candidato
        """)
    
    with col2:
        st.subheader("Atención 24/7")
        st.markdown("""
        - Respuestas inmediatas a consultas
        - Información precisa y actualizada
        - Experiencia personalizada
        """)

elif opcion == "Formulario de Contacto de Candidato":
    st.header("Formulario de Contacto de Candidato")
    st.markdown("Complete el formulario para invitar a un candidato al proceso de selección.")
    mostrar_formulario_candidatos()
    
elif opcion == "Chatbot":
    st.header("Chatbot de Atención")
    st.markdown("Interactúa con nuestro chatbot para resolver dudas.")
    lanzar_chatbot()

# Pie de página
st.markdown("---")
st.markdown("© 2025 Adaptiera. Todos los derechos reservados.")

