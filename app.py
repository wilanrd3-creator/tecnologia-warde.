import streamlit as st
import urllib.parse
import sqlite3
from datetime import datetime
import time

# Intentamos importar la librería oficial de Groq
try:
    from groq import Groq
except ImportError:
    st.error("Falta instalar la librería de Groq. Asegúrate de añadir 'groq' en tu archivo requirements.txt de GitHub.")
    st.stop()

# ============================================================
# 1. CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Tecnología Warde | Oficial",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# 2. CSS GLOBAL MEJORADO
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Rajdhani:wght@400;600&display=swap');

    .stApp {
        background: linear-gradient(135deg, #0F111A 0%, #141828 50%, #0A0D16 100%);
        font-family: 'Rajdhani', sans-serif;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #10131f 0%, #0c0f1a 100%);
        border-right: 1px solid #00A8FF22;
    }

    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 1px;
    }

    .divider {
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, transparent, #00A8FF, #7B2FBE, transparent);
        border: none;
        margin: 24px 0;
        border-radius: 2px;
    }

    .service-card {
        background: rgba(0, 168, 255, 0.05);
        border: 1px solid rgba(0, 168, 255, 0.25);
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 14px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .service-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 4px; height: 100%;
        background: linear-gradient(180deg, #00A8FF, #7B2FBE);
        border-radius: 4px 0 0 4px;
    }
    .service-card:hover {
        border-color: rgba(0, 168, 255, 0.6);
        background: rgba(0, 168, 255, 0.10);
        transform: translateX(4px);
    }
    .service-title {
        color: #00A8FF;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.85rem;
        font-weight: 700;
        margin-bottom: 6px;
        text-transform: uppercase;
    }
    .service-desc {
        color: #cdd6f4;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .service-price {
        display: inline-block;
        margin-top: 8px;
        padding: 3px 12px;
        background: linear-gradient(90deg, #00A8FF22, #7B2FBE22);
        border: 1px solid #00A8FF55;
        border-radius: 20px;
        color: #00CFFF;
        font-size: 0.88rem;
        font-weight: 600;
    }

    .founder-card {
        background: rgba(123, 47, 190, 0.08);
        border: 1px solid rgba(123, 47, 190, 0.30);
        border-radius: 14px;
        padding: 20px 16px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .founder-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(123, 47, 190, 0.25);
    }
    .founder-avatar {
        width: 64px; height: 64px;
        border-radius: 50%;
        background: linear-gradient(135deg, #00A8FF, #7B2FBE);
        display: flex; align-items: center; justify-content: center;
        font-size: 28px;
        margin: 0 auto 12px auto;
    }
    .founder-name {
        color: #e0e6ff;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.80rem;
        font-weight: 700;
    }
    .founder-role {
        color: #888ea8;
        font-size: 0.83rem;
        margin-top: 6px;
        line-height: 1.4;
    }
    .founder-badge {
        display: inline-block;
        margin-top: 10px;
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-active { background: #00A8FF22; color: #00CFFF; border: 1px solid #00A8FF55; }
    .badge-protected { background: #7B2FBE22; color: #b57bee; border: 1px solid #7B2FBE55; }

    .stat-card {
        background: rgba(0,168,255,0.06);
        border: 1px solid rgba(0,168,255,0.20);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
    }
    .stat-number {
        font-family: 'Orbitron', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        background: linear-gradient(90deg, #00A8FF, #7B2FBE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label { color: #888ea8; font-size: 0.82rem; margin-top: 4px; }

    .testimonial-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.09);
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        position: relative;
    }
    .testimonial-card::before {
        content: '"';
        position: absolute;
        top: -10px; left: 16px;
        font-size: 3rem;
        color: #00A8FF44;
        font-family: serif;
        line-height: 1;
    }
    .testi-text { color: #cdd6f4; font-size: 0.93rem; font-style: italic; line-height: 1.5; }
    .testi-author { color: #00A8FF; font-weight: 600; font-size: 0.85rem; margin-top: 8px; }

    .garantia-box {
        background: linear-gradient(135deg, rgba(0,168,255,0.08), rgba(123,47,190,0.08));
        border: 1px solid rgba(0,168,255,0.30);
        border-radius: 14px;
        padding: 22px 24px;
        text-align: center;
    }

    .social-link {
        display: inline-block;
        padding: 8px 18px;
        border-radius: 8px;
        margin: 5px;
        font-size: 0.88rem;
        font-weight: 600;
        text-decoration: none;
        transition: all 0.25s;
        border: 1px solid rgba(255,255,255,0.15);
        color: #fff !important;
    }
    .social-link:hover { transform: translateY(-2px); filter: brightness(1.2); }

    .status-online {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: rgba(0,200,100,0.12);
        border: 1px solid rgba(0,200,100,0.35);
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.82rem;
        color: #00c864;
        font-weight: 600;
    }
    .dot-pulse {
        width: 8px; height: 8px;
        border-radius: 50%;
        background: #00c864;
        animation: pulse 1.5s infinite;
        display: inline-block;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.4; transform: scale(0.75); }
    }

    .footer {
        text-align: center;
        padding: 24px 0 8px;
        color: #4a5070;
        font-size: 0.82rem;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin-top: 30px;
    }
    .footer a { color: #00A8FF; text-decoration: none; }

    .stProgress > div > div { background: linear-gradient(90deg, #00A8FF, #7B2FBE) !important; }

    [data-testid="stMetric"] {
        background: rgba(0,168,255,0.06);
        border: 1px solid rgba(0,168,255,0.18);
        border-radius: 10px;
        padding: 12px 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 3. SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(
        "<h3 style='color:#00A8FF; font-family:Orbitron,sans-serif; font-size:1rem;'>NAVEGACION RAPIDA</h3>",
        unsafe_allow_html=True,
    )
    st.markdown("- Servicios")
    st.markdown("- Metodos de Pago")
    st.markdown("- Junta Directiva")
    st.markdown("- Chat IA 24/7")
    st.markdown("- Comunidad")
    st.markdown("- Contacto")
    st.markdown("- FAQ")

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown(
        "<p style='color:#888ea8; font-size:0.78rem; text-transform:uppercase; letter-spacing:1px;'>Estado del Sistema</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='status-online'><span class='dot-pulse'></span> Todos los sistemas activos</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown(
        "<p style='color:#888ea8; font-size:0.78rem; text-transform:uppercase; letter-spacing:1px;'>Horario de Atencion</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#cdd6f4; font-size:0.85rem;'>Lunes - Viernes: 9am - 8pm<br>Sabado: 10am - 5pm<br>Domingo: Solo IA 24/7</p>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    if "visita_contada" not in st.session_state:
        st.session_state.visita_contada = True
        if "total_visitas" not in st.session_state:
            st.session_state.total_visitas = 1
        else:
            st.session_state.total_visitas += 1

    st.markdown(
        f"<p style='color:#4a5070; font-size:0.75rem; text-align:center;'>Visitas en esta sesion: {st.session_state.get('total_visitas', 1)}</p>",
        unsafe_allow_html=True,
    )

# ============================================================
# 4. BARRA DE CARGA INICIAL
# ============================================================
if "app_loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(
            "<p style='text-align:center; color:#00A8FF; font-family:Orbitron,sans-serif; font-size:0.9rem;'>Iniciando sistema Warde...</p>",
            unsafe_allow_html=True,
        )
        barra = st.progress(0)
        for i in range(0, 101, 20):
            time.sleep(0.07)
            barra.progress(i)
    placeholder.empty()
    st.session_state.app_loaded = True
    st.toast("Bienvenido a Tecnologia Warde! Estamos listos para servirte.")

# ============================================================
# 5. CABECERA PRINCIPAL
# ============================================================
st.markdown(
    """
    <div style='text-align:center; padding: 10px 0 4px;'>
        <div style='display:inline-block; padding:4px 18px; background:rgba(0,168,255,0.12);
                    border:1px solid rgba(0,168,255,0.40); border-radius:20px;
                    color:#00A8FF; font-size:0.75rem; font-family:Orbitron,sans-serif;
                    letter-spacing:2px; margin-bottom:14px;'>
            VERIFICADO | REPUBLICA DOMINICANA
        </div>
        <h1 style='color:#00A8FF; font-family:Orbitron,sans-serif;
                   font-size:2.4rem; margin:0; line-height:1.1;
                   text-shadow: 0 0 30px rgba(0,168,255,0.45);'>
            TECNOLOGIA WARDE
        </h1>
        <p style='color:#7B8DB0; font-size:1.05rem; margin-top:8px;'>
            Tu tecnologia en manos seguras &nbsp;|&nbsp; Republica Dominicana
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ============================================================
# 6. PRESENTACION DE LA EMPRESA
# ============================================================
st.info(
    "Bienvenido al futuro digital! En *Tecnologia Warde* transformamos tus ideas en realidad. "
    "Ofrecemos soluciones tecnologicas profesionales, desde optimizacion de plataformas hasta "
    "desarrollo web avanzado. **Todo 100% digital, rapido y sin salir de tu casa.**"
)

# ============================================================
# 7. METRICAS / ESTADISTICAS
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='color:#e0e6ff; font-family:Orbitron,sans-serif; font-size:1rem; text-align:center; letter-spacing:2px;'>NUMEROS QUE NOS RESPALDAN</h3>",
    unsafe_allow_html=True,
)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(label="Proyectos completados", value="0+", delta="Activos")
with col_m2:
    st.metric(label="Clientes satisfechos", value="0+", delta="Y creciendo")
with col_m3:
    st.metric(label="Servicios disponibles", value="100+", delta="Categorias")
with col_m4:
    st.metric(label="Disponibilidad IA", value="24/7", delta="Sin parar")

# ============================================================
# 8. CATALOGO DE SERVICIOS
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='color:#e0e6ff;'>Catalogo de Servicios</h2>",
    unsafe_allow_html=True,
)
st.write("Haz clic en cada categoria para ver los detalles y precios oficiales:")

with st.expander("MULTIMEDIA: Edicion de Video & YouTube"):
    st.markdown(
        """
        <div class='service-card'>
            <div class='service-title'>Edicion de Videos Cortos</div>
            <div class='service-desc'>Cortamos y optimizamos tus Reels, TikToks o Shorts con subtitulos dinamicos y musica en tendencia. Entrega rapida y revisiones incluidas.</div>
            <span class='service-price'>RD$ 100 - RD$ 150 por video</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Miniaturas de YouTube</div>
            <div class='service-desc'>Disenos con alto porcentaje de clics (CTR) para hacer crecer tu canal. Formato optimizado para todos los dispositivos.</div>
            <span class='service-price'>RD$ 150 por diseno</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("PROGRAMACION: Desarrollo Web Avanzado"):
    st.markdown(
        """
        <div class='service-card'>
            <div class='service-title'>Paginas Web en Python (Streamlit / Anvil)</div>
            <div class='service-desc'>Landing pages y sitios web modernos e interactivos para negocios. Incluye dominio configurado, diseno responsivo y soporte inicial.</div>
            <span class='service-price'>RD$ 700 - RD$ 1,000</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Configuracion de Servidores de Discord</div>
            <div class='service-desc'>Creacion completa con canales ordenados, roles personalizados, seguridad anti-spam y bots automatizados.</div>
            <span class='service-price'>RD$ 300 - RD$ 400</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("DISENO GRAFICO: Marca y Redes Sociales"):
    st.markdown(
        """
        <div class='service-card'>
            <div class='service-title'>Paquetes de Posts para Redes</div>
            <div class='service-desc'>Imagenes publicitarias personalizadas para Facebook o Instagram. Disenos coherentes con tu marca y en formato ideal para cada red.</div>
            <span class='service-price'>RD$ 150 - RD$ 300 por diseno</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Invitaciones Digitales</div>
            <div class='service-desc'>Tarjetas de cumpleanos o eventos listas para enviar por WhatsApp. Personalizadas con tu texto, colores e imagenes.</div>
            <span class='service-price'>RD$ 200 por diseno</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("Siguenos en Nuestras Redes Sociales"):
    st.markdown(
        """
        <div style='padding: 8px 0;'>
            <a href='https://www.facebook.com/profile.php?id=61591849505301' target='_blank'
               class='social-link' style='background:#1877F222; border-color:#1877F255;'>
               Facebook — Tecnologia Warde
            </a>
            <a href='https://www.instagram.com/tecnologiawarde/' target='_blank'
               class='social-link' style='background:#E1306C22; border-color:#E1306C55;'>
               Instagram — @tecnologiawarde
            </a>
            <a href='https://www.tiktok.com/@tecnologiawarde?lang=es-419' target='_blank'
               class='social-link' style='background:#69C9D022; border-color:#69C9D055;'>
               TikTok — @tecnologiawarde
            </a>
            <a href='https://discord.com/invite/vATQrTftJ' target='_blank'
               class='social-link' style='background:#5865F222; border-color:#5865F255;'>
               Discord — Unete al servidor
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 9. METODOS DE PAGO
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>Metodos de Pago</h2>", unsafe_allow_html=True)

col_pay1, col_pay2 = st.columns(2)
with col_pay1:
    st.success(
        "**Transacciones Seguras via Banco BHD:** Procesamos todos nuestros cobros "
        "de forma directa y transparente mediante transferencias bancarias dominicanas."
    )

# ============================================================
# 10. GARANTIA DE SERVICIO
# ============================================================
st.markdown(
    """
    <div class='garantia-box'>
        <p style='font-family:Orbitron,sans-serif; color:#00A8FF; font-size:0.9rem; margin-bottom:10px; letter-spacing:1px;'>
            GARANTIA WARDE
        </p>
        <p style='color:#cdd6f4; font-size:0.95rem; line-height:1.6; margin:0;'>
            Todos nuestros servicios incluyen <strong style='color:#00CFFF;'>revision ilimitada hasta tu aprobacion total</strong>.
            Si el resultado final no cumple lo acordado, lo corregimos sin costo adicional.
            Tu satisfaccion es nuestra prioridad.
        </p>
        <p style='color:#7B8DB0; font-size:0.80rem; margin-top:12px; margin-bottom:0;'>
            * Aplica dentro de los 7 dias siguientes a la entrega del proyecto.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 11. JUNTA DIRECTIVA
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>Junta Directiva</h2>", unsafe_allow_html=True)

col_fund1, col_fund2, col_fund3 = st.columns(3)

with col_fund1:
    st.markdown(
        """
        <div class='founder-card'>
            <div class='founder-avatar'>?</div>
            <div class='founder-name'>CEO 1</div>
            <div class='founder-role'>Vision de negocio y desarrollo. Prefiere mantener su identidad reservada.</div>
            <span class='founder-badge badge-protected'>Identidad Protegida</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_fund2:
    st.markdown(
        """
        <div class='founder-card'>
            <div class='founder-avatar' style='font-size:22px; font-family:Orbitron,sans-serif; color:#fff;'>LM</div>
            <div class='founder-name'>LIAM MULLER</div>
            <div class='founder-role'>Co-Fundador.</div>
            <span class='founder-badge badge-active'>Activo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_fund3:
    st.markdown(
        """
        <div class='founder-card'>
            <div class='founder-avatar' style='font-size:22px; font-family:Orbitron,sans-serif; color:#fff;'>DS</div>
            <div class='founder-name'>DAWEL SONYIS</div>
            <div class='founder-role'>FUNDADOR 3, Lider de las acciones y jefe del depto. de recursos humanos.</div>
            <span class='founder-badge badge-active'>Activo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 12. CHAT DE IA 24/7
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>Chat IA Warde — Disponible 24/7</h2>", unsafe_allow_html=True)
st.write("Nuestro asistente virtual esta activo a toda hora, incluso cuando el equipo humano no esta conectado:")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

SYSTEM_PROMPT = (
    "Eres el asistente virtual oficial de 'Tecnologia Warde', una empresa dominicana de servicios "
    "digitales (edicion de video, diseno grafico y desarrollo web). "
    "Responde siempre en espanol, de forma directa, profesional, amigable y en pocas lineas. "
    "Si no sabes algo con certeza, dilo y sugiere contactar a la Junta Directiva por el formulario de abajo.\n\n"
    "LISTA DE PRECIOS OFICIALES (en Pesos Dominicanos RD$):\n"
    "MULTIMEDIA:\n"
    "- Edicion de Videos Cortos (TikTok/Reels/Shorts con subtitulos): RD$ 100 - RD$ 150 por video\n"
    "- Miniaturas de YouTube: RD$ 150 por diseno\n"
    "PROGRAMACION:\n"
    "- Paginas Web en Python (Streamlit/Anvil): RD$ 700 - RD$ 1,000\n"
    "- Configuracion de Servidores de Discord (canales, roles, anti-spam, bots): RD$ 300 - RD$ 400\n"
    "DISENO GRAFICO:\n"
    "- Paquetes de Posts para Facebook/Instagram: RD$ 150 - RD$ 300 por diseno\n"
    "- Invitaciones Digitales: RD$ 200 por diseno\n\n"
    "METODO DE PAGO: transferencia bancaria directa por Banco BHD (Republica Dominicana).\n"
    "Toda contratacion o presupuesto final debe coordinarse con el Administrador Ejecutivo.\n\n"
    "INFORMACION DEL EQUIPO:\n"
    "Fundador 3: Dawel Sonyis — Fundador de Tecnologia Warde y mayor accionista. "
    "Administrador ejecutivo, lider de las acciones y jefe del departamento de recursos humanos.\n"
    "Fundador 2: Liam Muller — Desarrollador de Sistemas, Co-Fundador y Especialista en Optimizacion Tecnologica."
)

if "chat_historial" not in st.session_state:
    st.session_state.chat_historial = []

for autor, texto in st.session_state.chat_historial:
    with st.chat_message(autor):
        st.write(texto)

pregunta = st.chat_input("Escribe tu mensaje aqui... (Ej. Cuanto cuesta una pagina web?)")

if pregunta:
    st.session_state.chat_historial.append(("user", pregunta))
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        if not GROQ_API_KEY:
            respuesta = (
                "Hola! Soy el asistente virtual de Tecnologia Warde. Estoy en modo de demostracion "
                "porque aun no se ha configurado la clave 'GROQ_API_KEY' en Streamlit Cloud. "
                "Mientras tanto, puedes revisar el catalogo arriba o escribirnos por el formulario de contacto."
            )
            st.write(respuesta)
        else:
            with st.spinner("Pensando..."):
                try:
                    clave_limpia = str(GROQ_API_KEY).replace('"', "").replace("'", "").strip()
                    client = Groq(api_key=clave_limpia)
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
                            "He procesado muchas preguntas en las ultimas horas y estoy descansando "
                            "temporalmente. Intenta de nuevo en unos minutos o escribe directamente a la "
                            "Junta Directiva abajo."
                        )
                    else:
                        respuesta = (
                            "Los servidores de Groq estan procesando cambios en su red. "
                            "Intentalo de nuevo en breve."
                        )
                st.write(respuesta)

    st.session_state.chat_historial.append(("assistant", respuesta))

col_chat1, col_chat2 = st.columns([3, 1])
with col_chat2:
    if st.session_state.chat_historial:
        if st.button("Borrar conversacion", use_container_width=True):
            st.session_state.chat_historial = []
            st.rerun()

# ============================================================
# 13. CHAT GLOBAL DE LA COMUNIDAD
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>Chat Global de la Comunidad</h2>", unsafe_allow_html=True)
st.write("Deja tu mensaje para que lo vean todos los visitantes de la pagina:")

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
        (
            nombre.strip()[:40],
            mensaje.strip()[:300],
            datetime.now().strftime("%d/%m %H:%M"),
        ),
    )
    conn.commit()
    conn.close()

def borrar_mensaje(id_mensaje):
    conn = conectar_bd()
    conn.execute("DELETE FROM mensajes_globales WHERE id = ?", (id_mensaje,))
    conn.commit()
    conn.close()

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
        "Tu mensaje",
        max_chars=300,
        placeholder="Escribe algo para la comunidad...",
        height=80,
    )
    enviar = st.form_submit_button("Publicar mensaje")
    if enviar:
        if not nombre_visitante.strip() or not mensaje_visitante.strip():
            st.warning("Escribe tu nombre y un mensaje antes de publicar.")
        else:
            st.session_state.nombre_chat_global = nombre_visitante.strip()
            guardar_mensaje(nombre_visitante, mensaje_visitante)
            st.toast("Mensaje publicado con exito!")
            st.rerun()

col_actualizar, col_moderar = st.columns([1, 1])
with col_actualizar:
    if st.button("Actualizar mensajes", use_container_width=True):
        st.rerun()

mensajes = obtener_mensajes()
if not mensajes:
    st.info("Todavia no hay mensajes. Se el primero en escribir algo!")
else:
    for id_msg, nombre, texto, fecha in mensajes:
        with st.chat_message("user"):
            st.markdown(f"**{nombre}** · _{fecha}_")