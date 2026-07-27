import streamlit as st

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
    /* Estilo limpio para el botón de enviar sin romper el diseño */
    button[kind="primaryFormSubmit"], button[data-testid="stFormSubmitButton"] {
        border-radius: 8px !important;
        font-weight: bold !important;
        width: 100% !important;
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

col_fund1, col_fund2 = st.columns(2)

with col_fund1:
    st.markdown("### 👤 Fundador 1: Desconocido")
    st.caption("🔒 *Estatus: Identidad Protegida*")
    st.markdown("> **Pista:** *Dicen que su primer nombre es Wilan, tiene 12 años, un talento increíble para los negocios y programa desde las sombras en RD...* 🕵️‍♂️")

with col_fund2:
    st.markdown("### 👨‍💻 Fundador 2: Liam Muller")
    st.caption("⚡ *Estatus: Activo*")
    st.markdown("> **Rol:** *Desarrollador de Sistemas, Co-Fundador y Especialista en Optimización Tecnológica.* 🛠️")

st.write("---")

# 8. CHAT GLOBAL EN VIVO
st.header("💬 Chat Global de la Comunidad")
st.write("Habla en tiempo real con otros desarrolladores y clientes:")

# Base de datos en memoria para probar en tu computadora
if "mensajes_chat" not in st.session_state:
    st.session_state.mensajes_chat = [
        {"usuario": "Liam Muller", "texto": "¡Bienvenidos al chat oficial de la empresa! ⚡"},
        {"usuario": "Wilan", "texto": "¡Hola a todos! Lanzamos Tecnología Warde de forma oficial 🚀"}
    ]
