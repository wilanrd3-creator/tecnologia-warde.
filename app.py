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

# 8. Formulario de Contacto Interactivo Automatizado
st.header("📩 ¡Contáctanos y Cotiza tu Proyecto!")
st.write("Completa tus datos y nos comunicaremos contigo lo antes posible:")

# CAMBIA ESTE CORREO POR EL TUYO REAL PARA RECIBIR LOS MENSAJES DE TUS CLIENTES
tu_correo = "wilan@ejemplo.com" 

url_formulario = f"https://formsubmit.co{tu_correo}"

with st.form(key="formulario_contacto", clear_on_submit=True):
    nombre_cliente = st.text_input("👤 Tu Nombre Completo", placeholder="Ej. Juan Pérez")
    contacto_cliente = st.text_input("📱 Teléfono / WhatsApp", placeholder="Ej. 809-555-1234")
    
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
    
    boton_enviar = st.form_submit_button(label="🚀 Enviar Solicitud de Cotización", type="primary")

    if boton_enviar:
        if nombre_cliente == "" or contacto_cliente == "" or servicio_seleccionado == "Selecciona una opción...":
            st.error("⚠️ Por favor, llena los campos obligatorios (Nombre, Contacto y Servicio).")
        else:
            st.success("🎉 ¡Procesando envío! Serás redirigido para confirmar tu mensaje.")
            
            # Formulario oculto que se ejecuta en segundo plano para enviar la información a FormSubmit
            formulario_html = f"""
            <form id="click_form" action="{url_formulario}" method="POST" target="_self">
                <input type="hidden" name="Nombre" value="{nombre_cliente}">
                <input type="hidden" name="WhatsApp" value="{contacto_cliente}">
                <input type="hidden" name="Servicio" value="{servicio_seleccionado}">
                <input type="hidden" name="Detalles" value="{detalles_proyecto}">
                <input type="hidden" name="_captcha" value="false">
                <input type="hidden" name="_next" value="https://streamlit.app">
            </form>
            <script>document.getElementById("click_form").submit();</script>
            """
            st.markdown(formulario_html, unsafe_allow_html=True)
