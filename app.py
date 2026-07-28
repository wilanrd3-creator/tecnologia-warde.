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
    
    .faq-item {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 12px;
    }
    .faq-question {
        color: #00A8FF;
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .faq-answer {
        color: #cdd6f4;
        font-size: 0.9rem;
        line-height: 1.6;
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
        "<h3 style='color:#00A8FF; font-family:Orbitron,sans-serif; font-size:1rem;'>NAVEGACIÓN RÁPIDA</h3>",
        unsafe_allow_html=True,
    )
    
    # Menú de navegación clickeable
    menu_items = {
        "servicios": "Servicios",
        "pagos": "Métodos de Pago", 
        "fundadores": "Junta Directiva",
        "chat_ia": "Chat IA 24/7",
        "comunidad": "Comunidad",
        "faq": "FAQ"
    }
    
    for key, label in menu_items.items():
        st.markdown(f'<a href="#{key}" style="text-decoration:none; color:#cdd6f4;">📌 {label}</a>', unsafe_allow_html=True)

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
        "<p style='color:#888ea8; font-size:0.78rem; text-transform:uppercase; letter-spacing:1px;'>Horario de Atención</p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#cdd6f4; font-size:0.85rem;'>Lunes - Viernes: 9am - 8pm<br>Sábado: 10am - 5pm<br>Domingo: Solo IA 24/7</p>",
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
        f"<p style='color:#4a5070; font-size:0.75rem; text-align:center;'>Visitas en esta sesión: {st.session_state.get('total_visitas', 1)}</p>",
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
    st.toast("¡Bienvenido a Tecnología Warde! Estamos listos para servirte.")

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
            ✅ VERIFICADO | REPÚBLICA DOMINICANA
        </div>
        <h1 style='color:#00A8FF; font-family:Orbitron,sans-serif;
                   font-size:2.4rem; margin:0; line-height:1.1;
                   text-shadow: 0 0 30px rgba(0,168,255,0.45);'>
            TECNOLOGÍA WARDE
        </h1>
        <p style='color:#7B8DB0; font-size:1.05rem; margin-top:8px;'>
            Tu tecnología en manos seguras &nbsp;|&nbsp; República Dominicana
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

# ============================================================
# 6. PRESENTACIÓN DE LA EMPRESA
# ============================================================
st.info(
    "¡Bienvenido al futuro digital! En *Tecnología Warde* transformamos tus ideas en realidad. "
    "Ofrecemos soluciones tecnológicas profesionales, desde optimización de plataformas hasta "
    "desarrollo web avanzado. **Todo 100% digital, rápido y sin salir de tu casa.**"
)

# ============================================================
# 7. MÉTRICAS / ESTADÍSTICAS
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown(
    "<h3 style='color:#e0e6ff; font-family:Orbitron,sans-serif; font-size:1rem; text-align:center; letter-spacing:2px;'>NÚMEROS QUE NOS RESPALDAN</h3>",
    unsafe_allow_html=True,
)

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(label="Proyectos completados", value="50+", delta="Activos")
with col_m2:
    st.metric(label="Clientes satisfechos", value="30+", delta="Y creciendo")
with col_m3:
    st.metric(label="Servicios disponibles", value="10+", delta="Categorías")
with col_m4:
    st.metric(label="Disponibilidad IA", value="24/7", delta="Sin parar")

# ============================================================
# 8. CATÁLOGO DE SERVICIOS
# ============================================================
st.markdown("<div id='servicios' class='divider'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 style='color:#e0e6ff;'>Catálogo de Servicios</h2>",
    unsafe_allow_html=True,
)
st.write("Haz clic en cada categoría para ver los detalles y precios oficiales:")

with st.expander("🎬 MULTIMEDIA: Edición de Video & YouTube"):
    st.markdown(
        """
        <div class='service-card'>
            <div class='service-title'>Edición de Videos Cortos</div>
            <div class='service-desc'>Cortamos y optimizamos tus Reels, TikToks o Shorts con subtítulos dinámicos y música en tendencia. Entrega rápida y revisiones incluidas.</div>
            <span class='service-price'>RD$ 100 - RD$ 150 por video</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Miniaturas de YouTube</div>
            <div class='service-desc'>Diseños con alto porcentaje de clics (CTR) para hacer crecer tu canal. Formato optimizado para todos los dispositivos.</div>
            <span class='service-price'>RD$ 150 por diseño</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Edición de Videos Largos</div>
            <div class='service-desc'>Videos de 10-60 minutos con corrección de color, audio mejorado, cortes dinámicos y gráficos profesionales.</div>
            <span class='service-price'>RD$ 400 - RD$ 800 por video</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("💻 PROGRAMACIÓN: Desarrollo Web Avanzado"):
    st.markdown(
        """
        <div class='service-card'>
            <div class='service-title'>Páginas Web en Python (Streamlit / Anvil)</div>
            <div class='service-desc'>Landing pages y sitios web modernos e interactivos para negocios. Incluye dominio configurado, diseño responsivo y soporte inicial.</div>
            <span class='service-price'>RD$ 700 - RD$ 1,000</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Configuración de Servidores de Discord</div>
            <div class='service-desc'>Creación completa con canales ordenados, roles personalizados, seguridad anti-spam y bots automatizados.</div>
            <span class='service-price'>RD$ 300 - RD$ 400</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Automatización con Python</div>
            <div class='service-desc'>Scripts para automatizar tareas repetitivas, scraping web, procesamiento de datos y bots personalizados.</div>
            <span class='service-price'>RD$ 500 - RD$ 1,500</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("🎨 DISEÑO GRÁFICO: Marca y Redes Sociales"):
    st.markdown(
        """
        <div class='service-card'>
            <div class='service-title'>Paquetes de Posts para Redes</div>
            <div class='service-desc'>Imágenes publicitarias personalizadas para Facebook o Instagram. Diseños coherentes con tu marca y en formato ideal para cada red.</div>
            <span class='service-price'>RD$ 150 - RD$ 300 por diseño</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Invitaciones Digitales</div>
            <div class='service-desc'>Tarjetas de cumpleaños o eventos listas para enviar por WhatsApp. Personalizadas con tu texto, colores e imágenes.</div>
            <span class='service-price'>RD$ 200 por diseño</span>
        </div>
        <div class='service-card'>
            <div class='service-title'>Diseño de Logo Profesional</div>
            <div class='service-desc'>Logo único y memorable para tu marca. Incluye versiones en diferentes formatos y variaciones de color.</div>
            <span class='service-price'>RD$ 500 - RD$ 800</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

with st.expander("📱 Síguenos en Nuestras Redes Sociales"):
    st.markdown(
        """
        <div style='padding: 8px 0;'>
            <a href='https://www.facebook.com/profile.php?id=61591849505301' target='_blank'
               class='social-link' style='background:#1877F222; border-color:#1877F255;'>
               📘 Facebook — Tecnología Warde
            </a>
            <a href='https://www.instagram.com/tecnologiawarde/' target='_blank'
               class='social-link' style='background:#E1306C22; border-color:#E1306C55;'>
               📸 Instagram — @tecnologiawarde
            </a>
            <a href='https://www.tiktok.com/@tecnologiawarde?lang=es-419' target='_blank'
               class='social-link' style='background:#69C9D022; border-color:#69C9D055;'>
               🎵 TikTok — @tecnologiawarde
            </a>
            <a href='https://discord.com/invite/vATQrTftJ' target='_blank'
               class='social-link' style='background:#5865F222; border-color:#5865F255;'>
               💬 Discord — Únete al servidor
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 9. MÉTODOS DE PAGO
# ============================================================
st.markdown("<div id='pagos' class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>Métodos de Pago</h2>", unsafe_allow_html=True)

col_pay1, col_pay2 = st.columns(2)
with col_pay1:
    st.success(
        "**Transacciones Seguras vía Banco BHD:** Procesamos todos nuestros cobros "
        "de forma directa y transparente mediante transferencias bancarias dominicanas."
    )
with col_pay2:
    st.info(
        "**Proceso de pago:**\n"
        "1. Solicitas tu servicio\n"
        "2. Te enviamos los datos de la cuenta\n"  
        "3. Realizas el depósito/transferencia\n"
        "4. Envías el comprobante\n"
        "5. ¡Comenzamos tu proyecto!"
    )

# ============================================================
# 10. GARANTÍA DE SERVICIO
# ============================================================
st.markdown(
    """
    <div class='garantia-box'>
        <p style='font-family:Orbitron,sans-serif; color:#00A8FF; font-size:0.9rem; margin-bottom:10px; letter-spacing:1px;'>
            ⚡ GARANTÍA WARDE
        </p>
        <p style='color:#cdd6f4; font-size:0.95rem; line-height:1.6; margin:0;'>
            Todos nuestros servicios incluyen <strong style='color:#00CFFF;'>revisión ilimitada hasta tu aprobación total</strong>.
            Si el resultado final no cumple lo acordado, lo corregimos sin costo adicional.
            Tu satisfacción es nuestra prioridad.
        </p>
        <p style='color:#7B8DB0; font-size:0.80rem; margin-top:12px; margin-bottom:0;'>
            * Aplica dentro de los 7 días siguientes a la entrega del proyecto.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 11. JUNTA DIRECTIVA
# ============================================================
st.markdown("<div id='fundadores' class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>Junta Directiva</h2>", unsafe_allow_html=True)

col_fund1, col_fund2, col_fund3 = st.columns(3)

with col_fund1:
    st.markdown(
        """
        <div class='founder-card'>
            <div class='founder-avatar'>👤</div>
            <div class='founder-name'>CEO Estratégico</div>
            <div class='founder-role'>Visión de negocio y desarrollo. Prefiere mantener su identidad reservada.</div>
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
            <div class='founder-role'>Co-Fundador & Desarrollador de Sistemas. Especialista en Optimización Tecnológica.</div>
            <span class='founder-badge badge-active'>🟢 Activo</span>
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
            <div class='founder-role'>Fundador Principal, Mayor Accionista. Líder del departamento de Recursos Humanos.</div>
            <span class='founder-badge badge-active'>🟢 Activo</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 12. CHAT DE IA 24/7
# ============================================================
st.markdown("<div id='chat_ia' class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>🤖 Chat IA Warde — Disponible 24/7</h2>", unsafe_allow_html=True)
st.write("Nuestro asistente virtual está activo a toda hora, incluso cuando el equipo humano no está conectado:")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

SYSTEM_PROMPT = (
    "Eres el asistente virtual oficial de 'Tecnología Warde', una empresa dominicana de servicios "
    "digitales (edición de video, diseño gráfico y desarrollo web). "
    "Responde siempre en español, de forma directa, profesional, amigable y en pocas líneas. "
    "Si no sabes algo con certeza, dilo y sugiere contactar a la Junta Directiva por el formulario de abajo.\n\n"
    "LISTA DE PRECIOS OFICIALES (en Pesos Dominicanos RD$):\n"
    "MULTIMEDIA:\n"
    "- Edición de Videos Cortos (TikTok/Reels/Shorts con subtítulos): RD$ 100 - RD$ 150 por video\n"
    "- Miniaturas de YouTube: RD$ 150 por diseño\n"
    "- Edición de Videos Largos: RD$ 400 - RD$ 800 por video\n"
    "PROGRAMACIÓN:\n"
    "- Páginas Web en Python (Streamlit/Anvil): RD$ 700 - RD$ 1,000\n"
    "- Configuración de Servidores de Discord (canales, roles, anti-spam, bots): RD$ 300 - RD$ 400\n"
    "- Automatización con Python: RD$ 500 - RD$ 1,500\n"
    "DISEÑO GRÁFICO:\n"
    "- Paquetes de Posts para Facebook/Instagram: RD$ 150 - RD$ 300 por diseño\n"
    "- Invitaciones Digitales: RD$ 200 por diseño\n"
    "- Diseño de Logo Profesional: RD$ 500 - RD$ 800\n\n"
    "MÉTODO DE PAGO: transferencia bancaria directa por Banco BHD (República Dominicana).\n"
    "Toda contratación o presupuesto final debe coordinarse con el Administrador Ejecutivo.\n\n"
    "INFORMACIÓN DEL EQUIPO:\n"
    "Fundador 3: Dawel Sonyis — Fundador de Tecnología Warde y mayor accionista. "
    "Administrador ejecutivo, líder de las acciones y jefe del departamento de recursos humanos.\n"
    "Fundador 2: Liam Muller — Desarrollador de Sistemas, Co-Fundador y Especialista en Optimización Tecnológica."
)

if "chat_historial" not in st.session_state:
    st.session_state.chat_historial = []

for autor, texto in st.session_state.chat_historial:
    with st.chat_message(autor):
        st.write(texto)

pregunta = st.chat_input("Escribe tu mensaje aquí... (Ej. ¿Cuánto cuesta una página web?)")

if pregunta:
    st.session_state.chat_historial.append(("user", pregunta))
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        if not GROQ_API_KEY:
            respuesta = (
                "¡Hola! Soy el asistente virtual de Tecnología Warde. Estoy en modo de demostración "
                "porque aún no se ha configurado la clave 'GROQ_API_KEY' en Streamlit Cloud. "
                "Mientras tanto, puedes revisar el catálogo arriba o escribirnos por el formulario de contacto."
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
                            "He procesado muchas preguntas en las últimas horas y estoy descansando "
                            "temporalmente. Intenta de nuevo en unos minutos o escribe directamente a la "
                            "Junta Directiva abajo."
                        )
                    else:
                        respuesta = (
                            "Los servidores de Groq están procesando cambios en su red. "
                            "Inténtalo de nuevo en breve."
                        )
                st.write(respuesta)

    st.session_state.chat_historial.append(("assistant", respuesta))

col_chat1, col_chat2 = st.columns([3, 1])
with col_chat2:
    if st.session_state.chat_historial:
        if st.button("🗑️ Borrar conversación", use_container_width=True):
            st.session_state.chat_historial = []
            st.rerun()

# ============================================================
# 13. CHAT GLOBAL DE LA COMUNIDAD
# ============================================================
st.markdown("<div id='comunidad' class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>💬 Chat Global de la Comunidad</h2>", unsafe_allow_html=True)
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
    enviar = st.form_submit_button("📤 Publicar mensaje")
    if enviar:
        if not nombre_visitante.strip() or not mensaje_visitante.strip():
            st.warning("Escribe tu nombre y un mensaje antes de publicar.")
        else:
            st.session_state.nombre_chat_global = nombre_visitante.strip()
            guardar_mensaje(nombre_visitante, mensaje_visitante)
            st.toast("¡Mensaje publicado con éxito!")
            st.rerun()

col_actualizar, col_moderar = st.columns([1, 1])
with col_actualizar:
    if st.button("🔄 Actualizar mensajes", use_container_width=True):
        st.rerun()

mensajes = obtener_mensajes()
if not mensajes:
    st.info("Todavía no hay mensajes. ¡Sé el primero en escribir algo!")
else:
    for id_msg, nombre, texto, fecha in mensajes:
        with st.chat_message("user"):
            st.markdown(f"**{nombre}** · _{fecha}_")
            st.write(texto)

with col_moderar:
    with st.popover("🔧 Panel de moderación", use_container_width=True):
        clave_mod = st.text_input("Contraseña de moderador", type="password", key="clave_moderador")
        clave_correcta = st.secrets.get("MOD_PASSWORD")
        if clave_mod and clave_correcta and clave_mod == clave_correcta:
            st.success("✅ Acceso concedido.")
            for id_msg, nombre, texto, fecha in mensajes:
                col_txt, col_btn = st.columns([4, 1])
                col_txt.write(f"**{nombre}** ({fecha}): {texto[:60]}")
                if col_btn.button("❌", key=f"borrar_{id_msg}"):
                    borrar_mensaje(id_msg)
                    st.rerun()
        elif clave_mod:
            st.error("❌ Contraseña incorrecta.")

st.caption(
    "Este es un espacio público: cualquier visitante puede ver los mensajes. "
    "Nunca compartas tu dirección, contraseñas ni datos bancarios aquí."
)

# ============================================================
# 14. FAQ — PREGUNTAS FRECUENTES
# ============================================================
st.markdown("<div id='faq' class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 style='color:#e0e6ff;'>❓ Preguntas Frecuentes (FAQ)</h2>", unsafe_allow_html=True)

faqs = [
    (
        "¿Cuánto tiempo tarda en estar listo mi proyecto?",
        "Los tiempos varían según el servicio: edición de videos cortos (24-48 horas), diseños gráficos (24-72 horas) y páginas web (5-7 días hábiles). Te avisaremos antes de comenzar y te mantendremos informado durante todo el proceso.",
    ),
    (
        "¿Cómo se realiza el pago?",
        "A través de transferencia bancaria directa por Banco BHD. Una vez acordemos el servicio, te enviamos los datos de la cuenta para que realices el depósito o transferencia. Confirmamos con el comprobante y comenzamos de inmediato.",
    ),
    (
        "¿Qué pasa si no me gusta el resultado?",
        "Todos nuestros servicios incluyen revisiones ilimitadas hasta tu total aprobación. Si algo no cumple con lo acordado, lo corregimos sin costo adicional dentro de los 7 días siguientes a la entrega.",
    ),
    (
        "¿Trabajan con clientes fuera de República Dominicana?",
        "¡Por supuesto! Aunque estamos basados en República Dominicana, trabajamos con clientes de todo el mundo. Los pagos internacionales se pueden coordinar vía PayPal o Wise (TransferWise).",
    ),
    (
        "¿Necesito tener conocimientos técnicos para contratar una página web?",
        "No es necesario. Nosotros nos encargamos de todo el proceso técnico. Te entregamos el sitio listo para usar y te explicamos cómo administrarlo de forma sencilla si lo deseas.",
    ),
    (
        "¿Ofrecen facturación para empresas?",
        "Sí, podemos emitir comprobantes de venta para empresas dominicanas. Solo indícanos tus datos fiscales al momento de la contratación.",
    ),
    (
        "¿Puedo solicitar cambios después de entregado el proyecto?",
        "Sí, ofrecemos soporte post-entrega. Los cambios menores están incluidos en la garantía. Para modificaciones mayores o nuevas funcionalidades, podemos cotizarlas por separado.",
    ),
    (
        "¿Cómo contacto directamente a la Junta Directiva?",
        "Puedes escribirnos por cualquiera de nuestras redes sociales (Instagram, Facebook, TikTok) o unirte a nuestro servidor de Discord. También puedes consultar con nuestro chat de IA que te guiará en el proceso.",
    ),
]

for pregunta, respuesta in faqs:
    st.markdown(
        f"""
        <div class='faq-item'>
            <div class='faq-question'>❓ {pregunta}</div>
            <div class='faq-answer'>{respuesta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 15. FOOTER
# ============================================================
st.markdown(
    """
    <div class='footer'>
        <p style='color:#00A8FF; font-family:Orbitron,sans-serif; font-size:1rem; margin-bottom:8px;'>
            TECNOLOGÍA WARDE
        </p>
        <p>República Dominicana | Tecnología en manos seguras</p>
        <p style='margin-top:12px;'>
            <a href='https://www.facebook.com/profile.php?id=61591849505301' target='_blank'>Facebook</a> • 
            <a href='https://www.instagram.com/tecnologiawarde/' target='_blank'>Instagram</a> • 
            <a href='https://www.tiktok.com/@tecnologiawarde' target='_blank'>TikTok</a> • 
            <a href='https://discord.com/invite/vATQrTftJ' target='_blank'>Discord</a>
        </p>
        <p style='margin-top:16px; font-size:0.75rem; color:#4a5070;'>
            © 2025 Tecnología Warde. Todos los derechos reservados.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)