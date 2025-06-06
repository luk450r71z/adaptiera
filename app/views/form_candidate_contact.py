import streamlit as st
from utils.type_utils import validar_email, validar_telefono
from services.api_client import obtener_vacantes_extra, obtener_medios_extra
from services.email_sender import enviar_correo
from services.email_templates import generar_asunto_y_cuerpo_simple
from services.sms_sender import enviar_sms
from services.url_shortener import acortar_url, generar_url_token
#Cryptography
import json
from cryptography.fernet import Fernet
from core.config import settings

# Constantes
BASE_URL = "https://chatbot-adaptiera.streamlit.app"

def mostrar_formulario():
    """
    Muestra y maneja el formulario de invitación a postulación.
    """
    

    # Estado del botón para evitar múltiples envíos simultáneos
    if "enviando" not in st.session_state:
        st.session_state["enviando"] = False

    # Campos del formulario
    with st.form("formulario_invitacion_postulacion"):
        nombre = st.text_input("Apellidos y Nombres", placeholder="Ej. Juan Pérez")

        # Dropdown de Vacantes
        vacantes_base = ['Full Stack Developer', 'Datascience']
        vacantes_extra = obtener_vacantes_extra()
        opciones_vacantes = vacantes_base + vacantes_extra

        # Crear diccionario con índices
        vacantes_con_indices = {f"{i}: {vacante}": vacante for i, vacante in enumerate(opciones_vacantes)}
        vacante_seleccionada = st.selectbox("Vacante", list(vacantes_con_indices.keys()))

        correo = st.text_input("Correo", placeholder="ejemplo@dominio.com")
        telefono = st.text_input("Teléfono", placeholder="+52 123 456 7890")
        telefono = telefono.replace(" ", "")  # Limpia espacios antes de validación

        # Dropdown de Medio de Notificación
        medios_base = ['Correo', 'Teléfono']  # Primera letra en mayúscula
        medios_extra = [medio.capitalize() for medio in obtener_medios_extra()]  # Convertir primera letra a mayúscula
        opciones_medios = medios_base + medios_extra
        medio_notif = st.selectbox("Medio de Notificación", opciones_medios)

        submitted = st.form_submit_button("Enviar", disabled=st.session_state["enviando"])

    # Lógica de envío
    if submitted:
        st.session_state["enviando"] = True
        errores = []

        # Validaciones según el medio
        if medio_notif == 'Correo' and not validar_email(correo):
            errores.append("Correo inválido.")
        if medio_notif == 'Teléfono' and not validar_telefono(telefono):
            errores.append("Teléfono inválido (debe tener al menos 10 dígitos en formato internacional).")

        if errores:
            for error in errores:
                st.error(error)
            st.session_state["enviando"] = False
        else:
            vacante = vacantes_con_indices[vacante_seleccionada]

            # Generar una clave de cifrado
            key = Fernet.generate_key()
            cipher = Fernet(settings.FERNET_KEY)
            
            # Ejemplo de objeto JSON
            objeto_json = {
                "nombre": nombre,
                "phone": telefono,
                "vacancy": 1
            }

            # Convertir el objeto JSON a string
            json_string = json.dumps(objeto_json)

            # Encriptar el string
            json_encriptado = cipher.encrypt(json_string.encode())
            
            # Convertir a string para usarlo en la URL
            token = json_encriptado.decode()
            
            # Generar URL acortada
            enlace_entrevista = generar_url_token(BASE_URL, token)
            
            # Mostrar la URL para depuración
            st.session_state['last_token'] = token[:20] + "..." if len(token) > 20 else token
            st.session_state['last_url'] = enlace_entrevista

            with st.spinner("📤 Enviando notificación..."):
                notificacion_enviada = False

                if medio_notif == 'Correo':
                    # 1. Enviar correo interno
                    correo_interno_enviado = enviar_correo(
                        destinatario=correo,
                        asunto=f"👋 Te estamos buscando para el puesto de {vacante}",
                        cuerpo=f"""
                        Apellidos y Nombres: {nombre}
                        Vacante: {vacante}
                        Correo: {correo}
                        Teléfono: {telefono}
                        Medio de Notificación: {medio_notif}
                        Enlace de entrevista: {enlace_entrevista}
                        """
                    )

                    # 2. Enviar correo al candidato
                    if correo_interno_enviado:
                        try:
                            asunto_reclutamiento, cuerpo_reclutamiento = generar_asunto_y_cuerpo_simple(
                                nombre_candidato=nombre,
                                puesto=vacante,
                                empresa="Adaptiera",
                                enlace_entrevista=enlace_entrevista
                            )
                            notificacion_enviada = enviar_correo(
                                destinatario=correo,
                                asunto=asunto_reclutamiento,
                                cuerpo=cuerpo_reclutamiento
                            )
                        except Exception as e:
                            st.error(f"Error al generar o enviar correo de reclutamiento: {e}")

                    # Mostrar resultados de notificación por correo
                    if correo_interno_enviado:
                        st.success("✅ Formulario enviado correctamente.")
                        if notificacion_enviada:
                            st.success("✅ Correo de reclutamiento enviado al candidato.")
                        else:
                            st.warning("⚠️ No se pudo enviar el correo de reclutamiento al candidato.")
                    else:
                        st.error("❌ Hubo un error al enviar el correo interno.")

                elif medio_notif == 'Teléfono':
                    try:
                        mensaje_sms = f"Hola {nombre}, en Adaptiera queremos invitarte a postular al puesto de {vacante}. Ingresa aquí: {enlace_entrevista}"
                        mensaje_sms = f"Hola {nombre}, Somos Adaptiera!. Ingresa aquí: {enlace_entrevista}"
                        notificacion_enviada = enviar_sms(telefono, mensaje_sms)
                        st.success("✅ SMS enviado correctamente al candidato.")
                    except Exception as e:
                        st.error(f"❌ Error al enviar SMS: {e}")

                else:
                    st.info(f"📋 Medio de notificación no manejado: {medio_notif}")

            # Mostrar URL generada (para depuración)
            if 'last_url' in st.session_state:
                with st.expander("🔗 Detalles del enlace (para depuración)"):
                    st.write(f"Token original (truncado): {st.session_state['last_token']}")
                    st.write(f"URL generada: {st.session_state['last_url']}")
                    
            st.session_state["enviando"] = False

# Si el archivo se ejecuta directamente, muestra el formulario
if __name__ == "__main__":
    st.set_page_config(page_title="Adaptiera - Formulario de Invitación a Postulación", layout="centered")
    mostrar_formulario()