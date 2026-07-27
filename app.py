import streamlit as st
import urllib.parse
import sqlite3
from datetime import datetime

# Intentamos importar la librería oficial de Groq
try:
    from groq import Groq
except ImportError:
    st.error("⚠️ Falta instalar la librería de Groq. Asegúrate de añadir 'groq' en tu archivo requirements.txt de GitHub.")
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
    st.write("⚡ **Edición de Videos Cortos:** Cortamos y optimizamos tus Reels, TikToks o Shorts con subtítulos dinámicos y música en tendencia. *(RD$ 100 - RD$ 150 por video)*")
    st.write("🎨 **Miniaturas de YouTube:** Diseños con alto porcentaje de clics para hacer crecer tu canal. *(RD$ 150 por diseño)*")

with st.expander("💻 PROGRAMACIÓN: Desarrollo Web Avanzado"):
    st.write("🔥 **Páginas Web en Python (Streamlit/Anvil):** Landing pages y sitios web modernos e interactivos para negocios. *(RD$ 700 - RD$ 1,000)*")
    st.write("🛠️ **Configuración de Servidores de Discord:** Creación completa con canales ordenados, roles, seguridad anti-spam y bots. *(RD$ 300 - RD$ 400)*")

with st.expander("🎨 DISEÑO GRÁFICO: Marca y Redes Sociales"):
    st.write("📸 **Paquetes de Posts:** Imágenes publicitarias personalizadas para Facebook o Instagram. *(RD$ 150 - RD$ 300 por diseño)*")
    st.write("✉️ **Invitaciones Digitales:** Tarjetas de cumpleaños o eventos listas para enviar por WhatsApp. *(RD$ 200 por diseño)*")

with st.expander("🔗 Síguenos en Nuestras Redes Sociales"):
    st.write("👍 **Facebook:** [Tecnología Warde](https://www.facebook.com/profile.php?id=61591849505301)")
    st.write("📱 **Instagram:** [@tecn.ologia891](https://www.instagram.com/tecn.ologia891/)")
    st.write("🎵 **TikTok:** [@tecnologiawarde](https://www.tiktok.com/@tecnologiawarde?lang=es-419)")
    st.write("🎮 **Discord:** [Únete a nuestro servidor](https://discord.com/invite/vATQrTftJ)")

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
    st.markdown("### 👨‍💻 Fundador 2: Liam muller")
    st.caption("🔒 *Estatus: Activo*")
    st.markdown("> **Rol:** *Desarrollador de Sistemas, Co-Fundador y Especialista en Optimización Tecnológica.* 🛠️")

with col_fund3:
    st.markdown("### 👨‍💼 Fundador 3: Dawel Sonyis")
    st.caption("⚡ *Estatus: Activo*")
    st.markdown("> **Rol:** *Administrador ejecutivo, Líder de las acciones y jefe del departamento de recursos humanos.* 🛠️")

st.write("---")

# === SECCIÓN: CHAT DE IA 24/7 (CON HISTORIAL, ESTILO ASISTENTE VIRTUAL) ===
st.header("🤖 Chat IA Warde — Disponible 24/7")
st.write("Nuestro asistente virtual está activo a toda hora, incluso cuando el equipo humano no está conectado:")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

SYSTEM_PROMPT = (
    "Eres el asistente virtual oficial de 'Tecnología Warde', una empresa dominicana de servicios "
    "digitales (edición de video, diseño gráfico y desarrollo web). "
    "Responde siempre en español, de forma directa, profesional, amigable y en pocas líneas. "
    "Si no sabes algo con certeza, dilo y sugiere contactar a la Junta Directiva por el formulario de abajo.\n\n"
    "LISTA DE PRECIOS OFICIALES (en Pesos Dominicanos RD$), úsala siempre que te pregunten precios:\n"
    "MULTIMEDIA:\n"
    "- Edición de Videos Cortos (TikTok/Reels/Shorts con subtítulos): RD$ 100 - RD$ 150 por video\n"
    "- Miniaturas de YouTube: RD$ 150 por diseño\n"
    "PROGRAMACIÓN:\n"
    "- Páginas Web en Python (Streamlit/Anvil): RD$ 700 - RD$ 1,000\n"
    "- Configuración de Servidores de Discord (canales, roles, anti-spam, bots): RD$ 300 - RD$ 400\n"
    "DISEÑO GRÁFICO:\n"
    "- Paquetes de Posts para Facebook/Instagram: RD$ 150 - RD$ 300 por diseño\n"
    "- Invitaciones Digitales: RD$ 200 por diseño\n\n"
    "MÉTODO DE PAGO: transferencia bancaria directa por Banco BHD (República Dominicana).\n"
    "Toda contratación o presupuesto final debe coordinarse con el Administrador Ejecutivo de la empresa."
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
        if not GROQ_API_KEY:
            respuesta = (
                "👋 ¡Hola! Soy el asistente virtual de Tecnología Warde. Estoy en modo de demostración "
                "porque aún no se ha configurado la clave 'GROQ_API_KEY' en Streamlit Cloud. "
                "Mientras tanto, puedes revisar el catálogo arriba o escribirnos por el formulario de contacto."
            )
            st.write(respuesta)
        else:
            with st.spinner("⚡ Pensando..."):
                try:
                    clave_limpia = str(GROQ_API_KEY).replace('"', '').replace("'", "").strip()
                    client = Groq(api_key=clave_limpia)

                    # Construimos el historial en el formato que espera la API de Groq (estilo OpenAI),
                    # para que la IA recuerde el contexto de la conversación
                    mensajes = [{"role": "system", "content": SYSTEM_PROMPT}]
                    for autor_previo, texto_previo in st.session_state.chat_historial[:-1]:
                        rol = "user" if autor_previo == "user" else "assistant"
                        mensajes.append({"role": rol, "content": texto_previo})
                    mensajes.append({"role": "user", "content": pregunta})

                    response = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=mensajes,
                    )

                    respuesta = response.choices[0].message.content

                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "rate_limit" in error_str.lower():
                        respuesta = (
                            "⏳ He procesado muchas preguntas en las últimas horas y estoy descansando "
                            "temporalmente. Intenta de nuevo en unos minutos o escribe directamente a la "
                            "Junta Directiva abajo."
                        )
                    else:
                        respuesta = (
                            "⚠️ Los servidores de Groq están procesando cambios en su red. "
                            "Inténtalo de nuevo en breve."
                        )

                st.write(respuesta)

        st.session_state.chat_historial.append(("assistant", respuesta))

if st.session_state.chat_historial:
    if st.button("🗑️ Borrar conversación"):
        st.session_state.chat_historial = []
        st.rerun()

st.write("---")

# === SECCIÓN: CHAT GLOBAL DE LA COMUNIDAD (VISIBLE PARA TODOS LOS VISITANTES) ===
st.header("🌎 Chat Global de la Comunidad")
st.write("Deja tu mensaje para que lo vean todos los visitantes de la página:")

DB_PATH = "chat_global.db"


def conectar_bd():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mensajes_globales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


def obtener_mensajes(limite=50):
    conn = conectar_bd()
    filas = conn.execute(
        "SELECT id, nombre, mensaje, fecha FROM mensajes_globales ORDER BY id DESC LIMIT ?",
        (limite,),
    ).fetchall()
    conn.close()
    return list(reversed(filas))


def guardar_mensaje(nombre, mensaje):
    conn = conectar_bd()
    conn.execute(
        "INSERT INTO mensajes_globales (nombre, mensaje, fecha) VALUES (?, ?, ?)",
        (nombre.strip()[:40], mensaje.strip()[:300], datetime.now().strftime("%d/%m %H:%M")),
    )
    conn.commit()
    conn.close()


def borrar_mensaje(id_mensaje):
    conn = conectar_bd()
    conn.execute("DELETE FROM mensajes_globales WHERE id = ?", (id_mensaje,))
    conn.commit()
    conn.close()


# Recordamos el nombre del visitante durante su sesión, para no pedirlo cada vez
if "nombre_chat_global" not in st.session_state:
    st.session_state.nombre_chat_global = ""

with st.form("form_chat_global", clear_on_submit=True):
    nombre_visitante = st.text_input(
        "Tu nombre o apodo",
        value=st.session_state.nombre_chat_global,
        max_chars=40,
        placeholder="Ej. Ana desde Santiago",
    )
    mensaje_visitante = st.text_area(
        "Tu mensaje", max_chars=300, placeholder="Escribe algo para la comunidad...", height=80
    )
    enviar = st.form_submit_button("📨 Publicar mensaje")

    if enviar:
        if not nombre_visitante.strip() or not mensaje_visitante.strip():
            st.warning("⚠️ Escribe tu nombre y un mensaje antes de publicar.")
        else:
            st.session_state.nombre_chat_global = nombre_visitante.strip()
            guardar_mensaje(nombre_visitante, mensaje_visitante)
            st.rerun()

col_actualizar, col_moderar = st.columns([1, 1])
with col_actualizar:
    if st.button("🔄 Actualizar mensajes", use_container_width=True):
        st.rerun()

# Mostramos los mensajes más recientes, estilo muro público
mensajes = obtener_mensajes()

if not mensajes:
    st.info("Todavía no hay mensajes. ¡Sé el primero en escribir algo! 👋")
else:
    for id_msg, nombre, texto, fecha in mensajes:
        with st.chat_message("user"):
            st.markdown(f"**{nombre}** · _{fecha}_")
            st.write(texto)

# Panel de moderación protegido con contraseña, solo para el equipo de Tecnología Warde
with col_moderar:
    with st.popover("🛡️ Panel de moderación", use_container_width=True):
        clave_mod = st.text_input("Contraseña de moderador", type="password", key="clave_moderador")
        clave_correcta = st.secrets.get("MOD_PASSWORD")
        if clave_mod and clave_correcta and clave_mod == clave_correcta:
            st.success("Acceso concedido.")
            for id_msg, nombre, texto, fecha in mensajes:
                col_txt, col_btn = st.columns([4, 1])
                col_txt.write(f"**{nombre}** ({fecha}): {texto[:60]}")
                if col_btn.button("🗑️", key=f"borrar_{id_msg}"):
                    borrar_mensaje(id_msg)
                    st.rerun()
        elif clave_mod:
            st.error("Contraseña incorrecta.")

st.caption(
    "⚠️ Este es un espacio público: cualquier visitante puede ver los mensajes. "
    "Nunca compartas tu dirección, contraseñas ni datos bancarios aquí."
)

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