import streamlit as st
import requests
import urllib.parse

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
st.info("👋 **¡Bienvenido al futuro digital!** En *Tecnología Warde* transformamos tus ideas en realidad. Ofrecemos soluciones tecnológicas profesionales, desde optimización de plataformas hasta desarrollo web avanzado. **Todo 100% digital, rápido y sin salir de tu casa.**")

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
    st.markdown("### 👤 Fundador 1: Desconocido")
    st.caption("🔒 *Estatus: Identidad Protegida*")
    st.markdown("> **Pista:** *Dicen que su primer nombre es Wilan, tiene 12 años, un talento increíble para los negocios y programa desde las sombras en RD...* 🕵️‍♂️")

with col_fund2:
    st.markdown("### 👨‍💻 Fundador 2: Liam Muller")
    st.caption("⚡ *Estatus: Activo*")
    st.markdown("> **Rol:** *Desarrollador de Sistemas, Co-Fundador y Especialista en Optimización Tecnológica.* 🛠️")

with col_fund3:
    st.markdown("### 👨‍💼 Fundador 3: Dawel Sonyis")
    st.caption("⚡ *Estatus: Activo*")
    st.markdown("> **Rol:** *Administrador ejecutivo, Líder de las acciones y jefe del departamento de recursos humanos.* 🛠️")

st.write("---")

# === SECCIÓN: CONSULTOR DE IA INTEGRADO (SISTEMA GEMINI 24/7 ULTRARRÁPIDO) ===
st.header("🤖 Consultor de Inteligencia Artificial Warde")
st.write("Pregúntale lo que quieras a nuestra IA de Google, activa y lista las 24 horas del día:")

# Buscamos la clave segura de Google Gemini
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = None

pregunta = st.text_input("💬 Escribe tu pregunta aquí:", placeholder="Ej. Dame una idea para un video de YouTube...")

if pregunta:
    if not GEMINI_API_KEY:
        st.warning("⚙️ La IA está en modo de demostración. Configura tu 'GEMINI_API_KEY' en Streamlit Cloud para activarla de forma permanente.")
        st.info("👋 ¡Hola! Soy el asistente virtual de Tecnología Warde. Cuando mi desarrollador Wilan conecte mi clave de Google, podré responderte al instante las 24/7.")
    else:
        st.write("⚡ *Consultando al cerebro de Google Gemini...*")
        
        # Conexión directa y veloz a la API oficial de Google AI
        url_gemini = f"https://googleapis.com{GEMINI_API_KEY}"
        
        contexto_empresa = (
            "Eres un asistente tecnológico experto, amigable y profesional para la empresa 'Tecnología Warde' de República Dominicana. "
            "Responde de forma concisa, amena y siempre en español dominicano o estándar neutro. "
            f"Pregunta del usuario: {pregunta}"
        )
        
        payload = {
            "contents": [{"parts": [{"text": contexto_empresa}]}]
        }
        
        try:
            response = requests.post(url_gemini, json=payload, timeout=10)
            resultado = response.json()
            
            # Extracción limpia del texto del formato oficial de Google
            respuesta_ia = resultado['candidates'][0]['content']['parts'][0]['text']
            
            st.success("🤖 **Respuesta de la IA:**")
            st.write(respuesta_ia)
            
        except Exception as e:
            st.error("⚠️ Hubo un problema al procesar la solicitud con Google AI. Inténtalo de nuevo en unos segundos.")

st.write("---")

# 8. Formulario de Contacto Interactivo (SISTEMA SEGURO POR WHATSAPP)
st.header("📩 ¡Contáctanos y Cotiza tu Proyecto!")
st.write("Completa tus datos para generar tu orden de servicio:")

# Cambia este número por tu WhatsApp real si es necesario (ej: "18298751503")
telefono_warde = "18298751503" 

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
    enlace_whatsapp = f"https://wa.me{telefono_warde}?text={mensaje_codificado}"
    
    st.write("")
    st.link_button("🚀 Enviar orden por WhatsApp", enlace_whatsapp, type="primary", use_container_width=True)
else:
    st.info("💡 Completa los campos de arriba (Nombre, Teléfono y Servicio) para habilitar el botón de envío por WhatsApp.")
