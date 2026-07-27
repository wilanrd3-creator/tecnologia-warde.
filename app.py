import streamlit as st
import urllib.parse

# Intentamos importar la librería oficial de Google AI
try:
    from google import genai
except ImportError:
    st.error("⚠️ Falta instalar la librería de Google. Asegúrate de añadir 'google-genai' en tu archivo requirements.txt de GitHub.")
    st.stop()

# 1. Configuración de pestaña con título y logo futurista
st.set_page_config(page_title="Tecnología Warde | Oficial", page_icon="⚡", layout="centered")

# 2. CONFIGURACIÓN DEL FONDO SEGURO (Nativo de Streamlit para proteger las letras)
st.markdown(
    """
    <style>
    /* Forzamos el tema oscuro oficial para que el sistema maneje el contraste de las letras de forma segura */
    .stApp {
        background-color: #0F111A;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 3. Banner de Bienvenida Estilizado
st.markdown("<h1 style='text-align: center; color: #00A8FF;'>🚀 TECNOLOGÍA WARDE</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #888888;'>Tu tecnología en manos seguras | República Dominicana 🇩🇴</h3>", unsafe_allow_html=True)
st.write("---")

# 4. Presentación de la Empresa
st.info("👋 **¡Bienvenido al futuro digital!** En *Tecnología Warde* transformamos tus ideas en reality. Ofrecemos soluciones tecnológicas profesionales, desde optimización de plataformas hasta desarrollo web avanzado. **Todo 100% digital, rápido y sin salir de tu casa.**")

st.write("")

# 5. Catálogo de Servicios con Bloques Desplegables
st.header("📋 Nuestro Catálogo de Servicios")
st.write("Haz clic en cada categoría para ver los detalles y precios oficiales:")

with st.expander("🎥 MULTIMEDIA: Edición de Video & YouTube"):
    st.write("⚡ **Edición de Videos Cortos:** Cortamos y optimizamos tus Reels, TikToks o Shorts con subtítulos dinámicos y música en tendencia. *(RD$ 250 - RD$ 400 por video)*")
    st.write("🎨 **Miniaturas de YouTube:** Diseños con alto porcentaje de clics para hacer crecer tu canal. *(RD$ 150 por diseño)*")

with st.expander("💻 PROGRAMACIÓN: Desarrollo Web Avanzado"):
    st.write("🔥 **Páginas Web con Python:** Creamos Landing Pages y aplicaciones web modernas utilizando código interactivo de última generación. *(RD$ 1,500 - RD$ 3,000)*")
    st.write("🛠️ **Soporte & Configuración:** Estructuración de servidores de Discord profesionales con bots automáticos y roles. *(RD$ 500 - RD$ 1,000)*")

with st.expander("🎨 DISEÑO GRÁFICO: Marca y Redes Sociales"):
    st.write("📸 **Paquetes para Instagram/Facebook:** Diseños personalizados en Canva para que tu negocio local destaque de la competencia. *(RD$ 150 - RD$ 300)*")
    st.write("✉️ **Invitaciones Digitales:** Tarjetas interactivas para eventos especiales listas para enviar por WhatsApp. *(RD$ 200)*")

st.write("")
st.write("---")

# 6. Pasarela de Pagos Segura
st.header("💳 Métodos de Pago")
st.success("🔒 **Transacciones Seguras vía Banco BHD:** Procesamos todos nuestros cobros de forma directa y transparente mediante transferencias bancarias dominicanas.")
st.warning("⚠️ **Aviso de Seguridad:** Toda contratación, presupuesto o detalle financiero debe ser coordinado bajo la supervisión directa de nuestros padres o tutores legales.")

st.write("---")

# 7. Sección de Fundadores Estructurada con Columnas
st.header("👥 Junta Directiva")

col_fund1, col_fund2, col_fund3 = st.columns(3)

with col_fund1:
    st.markdown("### 👤 Fundador 1")
    st.caption("🔒 *Estatus: Identidad Protegida*")
    st.markdown("> **Rol:** *Visión de negocio y desarrollo. Prefiere mantener su identidad reservada.* 🕵️")

with col_fund2:
    st.markdown("### 👨‍💻 Fundador 2: Liam Muller")
    st.caption("⚡ *Estatus: Activo*")
    st.markdown("> **Rol:** *Desarrollador de Sistemas, Co-Fundador y Especialista en Optimización Tecnológica.* 🛠️")

with col_fund3:
    st.markdown("### 👨‍💼 Fundador 3: Dawel Sonyis")
    st.caption("⚡ *Estatus: Activo*")
    st.markdown("> **Rol:** *Administrador ejecutivo, Líder de las acciones y jefe del departamento de recursos humanos.* 🛠️")

st.write("---")

# === SECCIÓN: CHAT DE IA 24/7 (CON HISTORIAL, ESTILO ASISTENTE VIRTUAL) ===
st.header("🤖 Chat IA Warde — Disponible 24/7")
st.write("Nuestro asistente virtual está activo a toda hora, incluso cuando el equipo humano no está conectado:")

GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

SYSTEM_PROMPT = (
    "Eres el asistente virtual oficial de 'Tecnología Warde', una empresa dominicana de servicios "
    "digitales (edición de video, diseño gráfico y desarrollo web). "
    "Responde siempre en español, de forma directa, profesional, amigable y en pocas líneas. "
    "Si te preguntan precios, usa el catálogo mostrado en la página. "
    "Si no sabes algo con certeza, dilo y sugiere contactar a la Junta Directiva por el formulario de abajo."
)

# Inicializamos el historial del chat en la sesión (se mantiene mientras el usuario navega)
if "chat_historial" not in st.session_state:
    st.session_state.chat_historial = []

# Mostramos el historial de la conversación
for autor, texto in st.session_state.chat_historial:
    with st.chat_message(autor):
        st.write(texto)

# Caja de entrada tipo chat, siempre disponible al final de la sección
pregunta = st.chat_input("Escribe tu mensaje aquí... (Ej. ¿Cuánto cuesta una página web?)")

if pregunta:
    st.session_state.chat_historial.append(("user", pregunta))
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        if not GEMINI_API_KEY:
            respuesta = (
                "👋 ¡Hola! Soy el asistente virtual de Tecnología Warde. Estoy en modo de demostración "
                "porque aún no se ha configurado la clave 'GEMINI_API_KEY' en Streamlit Cloud. "
                "Mientras tanto, puedes revisar el catálogo arriba o escribirnos por el formulario de contacto."
            )
            st.write(respuesta)
        else:
            with st.spinner("⚡ Pensando..."):
                try:
                    clave_limpia = str(GEMINI_API_KEY).replace('"', '').replace("'", "").strip()
                    client = genai.Client(api_key=clave_limpia)

                    # Construimos el historial en el formato que espera la API,
                    # para que la IA recuerde el contexto de la conversación
                    contenidos = [SYSTEM_PROMPT]
                    for autor_previo, texto_previo in st.session_state.chat_historial[:-1]:
                        prefijo = "Cliente" if autor_previo == "user" else "Asistente"
                        contenidos.append(f"{prefijo}: {texto_previo}")
                    contenidos.append(f"Cliente: {pregunta}")

                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents="\n".join(contenidos),
                    )

                    respuesta = response.text

                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                        respuesta = (
                            "⏳ He procesado muchas preguntas en las últimas horas y estoy descansando "
                            "temporalmente. Intenta de nuevo en unos minutos o escribe directamente a la "
                            "Junta Directiva abajo."
                        )
                    else:
                        respuesta = (
                            "⚠️ Los servidores de Google AI están procesando cambios en su red. "
                            "Inténtalo de nuevo en breve."
                        )

                st.write(respuesta)

        st.session_state.chat_historial.append(("assistant", respuesta))

if st.session_state.chat_historial:
    if st.button("🗑️ Borrar conversación"):
        st.session_state.chat_historial = []
        st.rerun()

st.write("---")

# 8. Formulario de Contacto Interactivo (SISTEMA SEGURO POR WHATSAPP)
st.header("📩 ¡Contáctanos y Cotiza tu Proyecto!")
st.write("Completa tus datos para generar tu orden de servicio:")

telefono_warde = "18094523054"

nombre_cliente = st.text_input("👤 Tu Nombre Completo", placeholder="Ej. Juan Pérez")
contacto_cliente = st.text_input("📱 Tu Teléfono / WhatsApp", placeholder="Ej. 809-555-1234")

servicio_seleccionado = st.selectbox(
    "🛠️ ¿Qué servicio necesitas?",
    [
        "Selecciona una opción...",
        "MULTIMEDIA: Edición de Video Corto",
        "MULTIMEDIA: Miniatura de YouTube",
        "PROGRAMACIÓN: Página Web con Python",
        "PROGRAMACIÓN: Soporte / Servidor de Discord",
        "DISEÑO: Paquete para Redes Sociales",
        "DISEÑO: Invitación Digital"
    ]
)

detalles_proyecto = st.text_area("✏️ Cuéntanos más detalles sobre tu idea", placeholder="Escribe aquí lo que necesitas...")

if nombre_cliente and contacto_cliente and servicio_seleccionado != "Selecciona una opción...":
    mensaje_texto = (
        f"🚀 *NUEVA SOLICITUD - TECNOLOGÍA WARDE*\n\n"
        f"👤 *Cliente:* {nombre_cliente}\n"
        f"📱 *Contacto:* {contacto_cliente}\n"
        f"🛠️ *Servicio:* {servicio_seleccionado}\n"
        f"✏️ *Detalles:* {detalles_proyecto}"
    )

    mensaje_codificado = urllib.parse.quote(mensaje_texto)
    enlace_whatsapp = f"https://wa.me/{telefono_warde}?text={mensaje_codificado}"

    st.write("")
    st.link_button("🚀 Enviar orden por WhatsApp", enlace_whatsapp, type="primary", use_container_width=True)
else:
    st.info("💡 Completa los campos de arriba (Nombre, Teléfono y Servicio) para habilitar el botón de envío por WhatsApp.")
