import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import sqlite3
import hmac
import random
import string
import csv
import io
from datetime import datetime
import time

# Intentamos importar la librería oficial de Groq
try:
    from groq import Groq
except ImportError:
    st.error("Falta instalar la librería de Groq. Asegúrate de añadir 'groq' en tu archivo requirements.txt de GitHub.")
    st.stop()

# ============================================================
# 0. CONFIGURACION CENTRAL DE SERVICIOS Y PRECIOS
#    Fuente unica de verdad: antes los precios estaban repetidos
#    (catalogo, chat IA, formulario) y podian desincronizarse si
#    se cambiaba uno y no los otros. Ahora el Cotizador Automatico
#    y el resto de la app leen de aqui.
# ============================================================
SERVICIOS = {
    "Edicion de Video Corto (TikTok/Reels/Shorts)": {"min": 100, "max": 150, "unidad": "por video"},
    "Miniatura de YouTube": {"min": 150, "max": 150, "unidad": "por diseno"},
    "Pagina Web (Streamlit/Anvil)": {"min": 700, "max": 1000, "unidad": "por proyecto"},
    "Servidor de Discord (canales, roles, bots)": {"min": 300, "max": 400, "unidad": "por proyecto"},
    "Paquete de Posts para Redes Sociales": {"min": 150, "max": 300, "unidad": "por diseno"},
    "Invitacion Digital": {"min": 200, "max": 200, "unidad": "por diseno"},
}

RECARGO_URGENCIA = {
    "Normal (5-7 dias)": 1.0,
    "Rapido (2-3 dias)": 1.15,
    "Urgente (24-48 horas)": 1.35,
}

# ============================================================
# 0B. BASE DE DATOS — una sola conexion cacheada para las 4 tablas
#     que alimentan los sistemas nuevos (mensajes, pedidos, resenas,
#     leads). Se define aqui arriba para que estas funciones esten
#     disponibles sin importar en que orden aparezcan las secciones
#     mas abajo en la pagina.
#
#     NOTA IMPORTANTE: en Streamlit Community Cloud el sistema de
#     archivos es efimero — este archivo .db se borra si la app se
#     reinicia o redepliega. Para persistencia real a largo plazo
#     conviene usar una base de datos externa (Supabase, Turso,
#     PostgreSQL, etc.).
# ============================================================
DB_PATH = "warde_datos.db"


@st.cache_resource
def obtener_conexion_bd():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mensajes_globales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TEXT NOT NULL,
            verificado INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    # Migracion suave: si la tabla ya existia de antes sin la columna
    # "verificado", la agregamos ahora sin perder los mensajes previos.
    try:
        conn.execute("ALTER TABLE mensajes_globales ADD COLUMN verificado INTEGER NOT NULL DEFAULT 0")
        conn.commit()
    except sqlite3.OperationalError:
        pass  # la columna ya existe
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            contacto TEXT NOT NULL,
            servicio TEXT NOT NULL,
            presupuesto TEXT,
            urgencia TEXT,
            detalles TEXT,
            estado TEXT NOT NULL DEFAULT 'Recibido',
            fecha TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS resenas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            comentario TEXT NOT NULL,
            estrellas INTEGER NOT NULL,
            aprobado INTEGER NOT NULL DEFAULT 0,
            fecha TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT NOT NULL,
            interes TEXT,
            fecha TEXT NOT NULL
        )
        """
    )
    # ---- Tablas del Modo Propietario (GOD) ----
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS baneados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor TEXT NOT NULL UNIQUE,
            motivo TEXT,
            fecha TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS visitas_globales (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    conn.execute("INSERT OR IGNORE INTO visitas_globales (id, total) VALUES (1, 0)")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS anuncio_fijado (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            texto TEXT,
            fecha TEXT
        )
        """
    )
    # ---- Consola del Modo Propietario (GOD): registro de eventos ----
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS log_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            detalle TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


# ---- Modo Propietario (GOD): consola de eventos en vivo ----
def registrar_evento(tipo, detalle):
    try:
        conn = obtener_conexion_bd()
        conn.execute(
            "INSERT INTO log_eventos (tipo, detalle, fecha) VALUES (?, ?, ?)",
            (tipo[:30], (detalle or "").strip()[:300], datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        )
        conn.commit()
        # La tabla de eventos no debe crecer sin limite: nos quedamos con los ultimos 500.
        conn.execute(
            "DELETE FROM log_eventos WHERE id NOT IN "
            "(SELECT id FROM log_eventos ORDER BY id DESC LIMIT 500)"
        )
        conn.commit()
    except Exception:
        pass  # la consola nunca debe romper la experiencia del usuario


def obtener_eventos(limite=150):
    conn = obtener_conexion_bd()
    return conn.execute(
        "SELECT tipo, detalle, fecha FROM log_eventos ORDER BY id DESC LIMIT ?", (limite,)
    ).fetchall()


def limpiar_eventos():
    conn = obtener_conexion_bd()
    conn.execute("DELETE FROM log_eventos")
    conn.commit()


# ---- Modo Propietario (GOD): visitas globales ----
def incrementar_visitas_globales():
    conn = obtener_conexion_bd()
    conn.execute("UPDATE visitas_globales SET total = total + 1 WHERE id = 1")
    conn.commit()


def obtener_visitas_globales():
    conn = obtener_conexion_bd()
    fila = conn.execute("SELECT total FROM visitas_globales WHERE id = 1").fetchone()
    return fila[0] if fila else 0


# ---- Modo Propietario (GOD): baneos ----
def banear_valor(valor, motivo=""):
    conn = obtener_conexion_bd()
    try:
        conn.execute(
            "INSERT INTO baneados (valor, motivo, fecha) VALUES (?, ?, ?)",
            (valor.strip()[:60], (motivo or "").strip()[:200], datetime.now().strftime("%d/%m/%Y %H:%M")),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # ya estaba baneado


def desbanear(id_baneo):
    conn = obtener_conexion_bd()
    conn.execute("DELETE FROM baneados WHERE id = ?", (id_baneo,))
    conn.commit()


def listar_baneados():
    conn = obtener_conexion_bd()
    return conn.execute("SELECT id, valor, motivo, fecha FROM baneados ORDER BY id DESC").fetchall()


def esta_baneado(valor):
    conn = obtener_conexion_bd()
    valor_normalizado = (valor or "").strip().lower()
    filas = conn.execute("SELECT valor FROM baneados").fetchall()
    return any(valor_normalizado == v[0].strip().lower() for v in filas)


# ---- Modo Propietario (GOD): anuncio fijado en el chat global ----
def guardar_anuncio(texto):
    conn = obtener_conexion_bd()
    conn.execute(
        "INSERT INTO anuncio_fijado (id, texto, fecha) VALUES (1, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET texto = excluded.texto, fecha = excluded.fecha",
        (texto.strip()[:300], datetime.now().strftime("%d/%m/%Y %H:%M")),
    )
    conn.commit()


def obtener_anuncio():
    conn = obtener_conexion_bd()
    fila = conn.execute("SELECT texto, fecha FROM anuncio_fijado WHERE id = 1").fetchone()
    return fila if fila and fila[0] else None


def borrar_anuncio():
    conn = obtener_conexion_bd()
    conn.execute("DELETE FROM anuncio_fijado WHERE id = 1")
    conn.commit()


# ---- Modo Propietario (GOD): estadisticas y limpieza masiva ----
def obtener_estadisticas_generales():
    conn = obtener_conexion_bd()
    total_mensajes = conn.execute("SELECT COUNT(*) FROM mensajes_globales").fetchone()[0]
    total_ordenes = conn.execute("SELECT COUNT(*) FROM ordenes").fetchone()[0]
    total_resenas = conn.execute("SELECT COUNT(*) FROM resenas").fetchone()[0]
    total_leads = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
    total_baneados = conn.execute("SELECT COUNT(*) FROM baneados").fetchone()[0]
    return {
        "mensajes": total_mensajes,
        "ordenes": total_ordenes,
        "resenas": total_resenas,
        "leads": total_leads,
        "baneados": total_baneados,
        "visitas": obtener_visitas_globales(),
    }


def borrar_todos_mensajes():
    conn = obtener_conexion_bd()
    conn.execute("DELETE FROM mensajes_globales")
    conn.commit()


def borrar_todas_ordenes():
    conn = obtener_conexion_bd()
    conn.execute("DELETE FROM ordenes")
    conn.commit()


def borrar_todos_leads():
    conn = obtener_conexion_bd()
    conn.execute("DELETE FROM leads")
    conn.commit()


def borrar_todas_resenas():
    conn = obtener_conexion_bd()
    conn.execute("DELETE FROM resenas")
    conn.commit()


# ---- Mensajes (chat global de la comunidad) ----
def obtener_mensajes(limite=50):
    conn = obtener_conexion_bd()
    filas = conn.execute(
        "SELECT id, nombre, mensaje, fecha, verificado FROM mensajes_globales ORDER BY id DESC LIMIT ?",
        (limite,),
    ).fetchall()
    return list(reversed(filas))


def guardar_mensaje(nombre, mensaje, verificado=False):
    conn = obtener_conexion_bd()
    conn.execute(
        "INSERT INTO mensajes_globales (nombre, mensaje, fecha, verificado) VALUES (?, ?, ?, ?)",
        (
            nombre.strip()[:40], mensaje.strip()[:300],
            datetime.now().strftime("%d/%m %H:%M"), int(bool(verificado)),
        ),
    )
    conn.commit()


def borrar_mensaje(id_mensaje):
    conn = obtener_conexion_bd()
    conn.execute("DELETE FROM mensajes_globales WHERE id = ?", (id_mensaje,))
    conn.commit()


# ---- Sistema 2: Seguimiento de Pedidos ----
def generar_codigo_orden():
    sufijo = "".join(random.choices(string.digits, k=4))
    return f"WARDE-{sufijo}"


def guardar_orden(nombre, contacto, servicio, presupuesto, urgencia, detalles):
    conn = obtener_conexion_bd()
    for _ in range(5):
        codigo = generar_codigo_orden()
        try:
            conn.execute(
                """
                INSERT INTO ordenes (codigo, nombre, contacto, servicio, presupuesto, urgencia, detalles, estado, fecha)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Recibido', ?)
                """,
                (
                    codigo, nombre.strip()[:60], contacto.strip()[:40], servicio,
                    presupuesto, urgencia, (detalles or "").strip()[:500],
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                ),
            )
            conn.commit()
            return codigo
        except sqlite3.IntegrityError:
            continue  # codigo duplicado (muy improbable): reintenta con otro
    return None


def obtener_orden_por_codigo(codigo):
    conn = obtener_conexion_bd()
    return conn.execute(
        "SELECT codigo, nombre, servicio, estado, fecha FROM ordenes WHERE codigo = ?",
        (codigo.strip().upper(),),
    ).fetchone()


def listar_ordenes(limite=100):
    conn = obtener_conexion_bd()
    return conn.execute(
        "SELECT id, codigo, nombre, servicio, estado, fecha FROM ordenes ORDER BY id DESC LIMIT ?",
        (limite,),
    ).fetchall()


def actualizar_estado_orden(id_orden, nuevo_estado):
    conn = obtener_conexion_bd()
    conn.execute("UPDATE ordenes SET estado = ? WHERE id = ?", (nuevo_estado, id_orden))
    conn.commit()


# ---- Sistema 3: Resenas reales de clientes ----
def guardar_resena(nombre, comentario, estrellas):
    conn = obtener_conexion_bd()
    conn.execute(
        "INSERT INTO resenas (nombre, comentario, estrellas, aprobado, fecha) VALUES (?, ?, ?, 0, ?)",
        (nombre.strip()[:40], comentario.strip()[:400], int(estrellas), datetime.now().strftime("%d/%m/%Y")),
    )
    conn.commit()


def obtener_resenas_aprobadas(limite=9):
    conn = obtener_conexion_bd()
    return conn.execute(
        "SELECT nombre, comentario, estrellas, fecha FROM resenas WHERE aprobado = 1 ORDER BY id DESC LIMIT ?",
        (limite,),
    ).fetchall()


def obtener_resenas_pendientes():
    conn = obtener_conexion_bd()
    return conn.execute(
        "SELECT id, nombre, comentario, estrellas, fecha FROM resenas WHERE aprobado = 0 ORDER BY id DESC"
    ).fetchall()


def moderar_resena(id_resena, aprobar):
    conn = obtener_conexion_bd()
    if aprobar:
        conn.execute("UPDATE resenas SET aprobado = 1 WHERE id = ?", (id_resena,))
    else:
        conn.execute("DELETE FROM resenas WHERE id = ?", (id_resena,))
    conn.commit()


# ---- Sistema 4: Captura de leads / lista de espera VIP ----
def guardar_lead(nombre, contacto, interes):
    conn = obtener_conexion_bd()
    conn.execute(
        "INSERT INTO leads (nombre, contacto, interes, fecha) VALUES (?, ?, ?, ?)",
        (nombre.strip()[:60], contacto.strip()[:60], interes, datetime.now().strftime("%d/%m/%Y %H:%M")),
    )
    conn.commit()


def listar_leads():
    conn = obtener_conexion_bd()
    return conn.execute("SELECT nombre, contacto, interes, fecha FROM leads ORDER BY id DESC").fetchall()

# ============================================================
# 1. CONFIGURACIÓN DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Tecnología Warde | Desarrollo Web, Diseño y Video en RD",
    page_icon=":zap:",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ============================================================
# 1B. SEO BÁSICO — meta description, OG tags y título de pestaña
# ============================================================
components.html(
    """
    <script>
        try {
            const doc = window.parent.document;
            doc.title = "Tecnología Warde | Desarrollo Web, Diseño y Video en RD";
            const metaTags = [
                {name: "description", content: "Tecnología Warde: edición de video, diseño gráfico y desarrollo web profesional en República Dominicana. Cotiza tu proyecto hoy mismo."},
                {property: "og:title", content: "Tecnología Warde"},
                {property: "og:description", content: "Servicios digitales profesionales en República Dominicana: video, diseño y desarrollo web."},
                {property: "og:type", content: "website"},
            ];
            metaTags.forEach(tagInfo => {
                const selector = tagInfo.name ? `meta[name="${tagInfo.name}"]` : `meta[property="${tagInfo.property}"]`;
                if (!doc.querySelector(selector)) {
                    const meta = doc.createElement('meta');
                    if (tagInfo.name) meta.setAttribute('name', tagInfo.name);
                    if (tagInfo.property) meta.setAttribute('property', tagInfo.property);
                    meta.setAttribute('content', tagInfo.content);
                    doc.head.appendChild(meta);
                }
            });
        } catch (e) {
            console.log('No se pudo inyectar metadata:', e);
        }
    </script>
    """,
    height=0,
)

# ============================================================
# 2. CSS GLOBAL MEJORADO — glassmorphism + animaciones + responsive
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

    h2 {
        position: relative;
        display: inline-block;
        padding-bottom: 8px;
        animation: fadeInUp 0.6s ease both;
    }
    h2::after {
        content: '';
        position: absolute;
        left: 0; bottom: 0;
        height: 3px;
        width: 46px;
        border-radius: 3px;
        background: linear-gradient(90deg, #00A8FF, #7B2FBE);
        transition: width 0.4s ease;
    }
    h2:hover::after { width: 100%; }
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
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
    .testi-stars { color: #f1c40f; font-size: 0.85rem; }

    .faq-item {
        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 10px;
    }

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
        50%       { opacity: 0.4; transform: scale(0.75); }
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

    @media (max-width: 640px) {
        h1 { font-size: 1.7rem !important; }
        .service-card, .founder-card, .testimonial-card { padding: 14px 14px; }
        .social-link { display: block; margin: 6px 0; text-align: center; }
        [data-testid="stMetric"] { padding: 8px 10px; }
    }

    .stApp {
        background-color: #0A0D16;
        background-image:
            radial-gradient(circle at 1px 1px, rgba(0,168,255,0.16) 1px, transparent 0),
            linear-gradient(135deg, #0F111A 0%, #141828 30%, #16112a 55%, #0A0D16 100%);
        background-size: 26px 26px, 300% 300%;
        animation: gradientShift 22s ease infinite;
    }
    @keyframes gradientShift {
        0%   { background-position: 0 0, 0% 50%; }
        50%  { background-position: 0 0, 100% 50%; }
        100% { background-position: 0 0, 0% 50%; }
    }
    @media (prefers-reduced-motion: reduce) {
        .stApp { animation: none; }
    }

    section.main > div.block-container {
        position: relative;
        z-index: 1;
    }
    section[data-testid="stSidebar"] { position: relative; z-index: 1; }

    html { scroll-behavior: smooth; }

    .brand-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.6rem;
        font-weight: 900;
        margin: 0;
        line-height: 1.1;
        letter-spacing: 3px;
        background: linear-gradient(90deg, #00A8FF, #7B2FBE, #00CFFF, #00A8FF);
        background-size: 300% auto;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 6s linear infinite;
        text-shadow: 0 0 40px rgba(0,168,255,0.25);
    }
    @keyframes shine {
        0%   { background-position: 0% 50%; }
        100% { background-position: 300% 50%; }
    }
    @media (max-width: 640px) {
        .brand-title { font-size: 1.9rem; letter-spacing: 1.5px; }
    }

    /* ---- NUEVO: cards de portafolio ---- */
    .portfolio-card {
        background: rgba(0,168,255,0.05);
        border: 1px solid rgba(0,168,255,0.22);
        border-radius: 14px;
        overflow: hidden;
        margin-bottom: 16px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .portfolio-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,168,255,0.20);
    }
    .portfolio-cover {
        height: 90px;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Orbitron', sans-serif;
        font-size: 1.6rem;
        color: #fff;
    }
    .portfolio-body { padding: 14px 16px; }
    .portfolio-tag {
        display: inline-block;
        font-size: 0.72rem;
        color: #00CFFF;
        background: #00A8FF1a;
        border: 1px solid #00A8FF44;
        border-radius: 20px;
        padding: 2px 10px;
        margin-bottom: 8px;
    }

    /* ---- NUEVO: linea de tiempo del proceso ---- */
    .timeline-wrap { position: relative; padding-left: 28px; }
    .timeline-wrap::before {
        content: '';
        position: absolute; left: 8px; top: 4px; bottom: 4px;
        width: 2px;
        background: linear-gradient(180deg, #00A8FF, #7B2FBE);
    }
    .timeline-step { position: relative; padding-bottom: 22px; }
    .timeline-step::before {
        content: '';
        position: absolute; left: -28px; top: 2px;
        width: 14px; height: 14px; border-radius: 50%;
        background: #0A0D16;
        border: 3px solid #00A8FF;
    }
    .timeline-title { color: #e0e6ff; font-family: 'Orbitron', sans-serif; font-size: 0.85rem; }
    .timeline-desc { color: #888ea8; font-size: 0.85rem; margin-top: 2px; }

    /* ---- NUEVO: cupon aplicado ---- */
    .cupon-badge {
        display: inline-block;
        background: rgba(0,200,100,0.14);
        border: 1px solid rgba(0,200,100,0.4);
        color: #00c864;
        border-radius: 20px;
        padding: 4px 14px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 2B. FONDO REAL — red de nodos conectados en el navegador
# ============================================================
components.html(
    """
    <script>
        try {
            const doc = window.parent.document;
            const win = window.parent;
            const canvasId = 'warde-network-canvas';

            if (!doc.getElementById(canvasId)) {
                const glowStyle = doc.createElement('style');
                glowStyle.id = 'warde-glow-style';
                glowStyle.innerHTML = `
                    #warde-glow-wrapper { position: fixed; inset: 0; z-index: 0; pointer-events: none; overflow: hidden; }
                    #warde-glow-wrapper .glow { position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0.20; }
                    #warde-glow-wrapper .glow-a { width: 480px; height: 480px; top: -180px; left: -160px; background: radial-gradient(circle, #00A8FF, transparent 70%); }
                    #warde-glow-wrapper .glow-b { width: 440px; height: 440px; bottom: -200px; right: -160px; background: radial-gradient(circle, #7B2FBE, transparent 70%); }
                `;
                doc.head.appendChild(glowStyle);
                const glowWrap = doc.createElement('div');
                glowWrap.id = 'warde-glow-wrapper';
                glowWrap.innerHTML = `<div class="glow glow-a"></div><div class="glow glow-b"></div>`;
                doc.body.appendChild(glowWrap);

                const canvas = doc.createElement('canvas');
                canvas.id = canvasId;
                canvas.style.position = 'fixed';
                canvas.style.inset = '0';
                canvas.style.zIndex = '0';
                canvas.style.pointerEvents = 'none';
                doc.body.appendChild(canvas);

                const ctx = canvas.getContext('2d');
                const colores = ['#00A8FF', '#7B2FBE', '#00CFFF'];
                const reduceMotion = win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches;

                let nodos = [];
                function resize() { canvas.width = win.innerWidth; canvas.height = win.innerHeight; }
                function crearNodos() {
                    const cantidad = Math.max(18, Math.min(42, Math.floor((win.innerWidth * win.innerHeight) / 45000)));
                    nodos = Array.from({ length: cantidad }, () => ({
                        x: Math.random() * canvas.width,
                        y: Math.random() * canvas.height,
                        vx: (Math.random() - 0.5) * 0.22,
                        vy: (Math.random() - 0.5) * 0.22,
                        r: Math.random() * 1.6 + 1.2,
                        color: colores[Math.floor(Math.random() * colores.length)],
                    }));
                }
                resize();
                crearNodos();
                const maxDist = 150;

                function dibujarFrame() {
                    ctx.clearRect(0, 0, canvas.width, canvas.height);
                    for (let i = 0; i < nodos.length; i++) {
                        for (let j = i + 1; j < nodos.length; j++) {
                            const a = nodos[i], b = nodos[j];
                            const dx = a.x - b.x, dy = a.y - b.y;
                            const dist = Math.sqrt(dx * dx + dy * dy);
                            if (dist < maxDist) {
                                ctx.strokeStyle = `rgba(0,168,255,${0.16 * (1 - dist / maxDist)})`;
                                ctx.lineWidth = 1;
                                ctx.beginPath();
                                ctx.moveTo(a.x, a.y);
                                ctx.lineTo(b.x, b.y);
                                ctx.stroke();
                            }
                        }
                    }
                    for (const n of nodos) {
                        ctx.beginPath();
                        ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
                        ctx.fillStyle = n.color;
                        ctx.globalAlpha = 0.55;
                        ctx.fill();
                        ctx.globalAlpha = 1;
                    }
                }

                function paso() {
                    for (const n of nodos) {
                        n.x += n.vx; n.y += n.vy;
                        if (n.x < 0 || n.x > canvas.width) n.vx *= -1;
                        if (n.y < 0 || n.y > canvas.height) n.vy *= -1;
                    }
                    dibujarFrame();
                    if (!reduceMotion) win.requestAnimationFrame(paso);
                }

                win.addEventListener('resize', function () {
                    resize(); crearNodos();
                    if (reduceMotion) dibujarFrame();
                });

                if (reduceMotion) { dibujarFrame(); } else { paso(); }
            }
        } catch (e) {
            console.log('No se pudo inyectar el fondo:', e);
        }
    </script>
    """,
    height=0,
)

# ============================================================
# 3. SIDEBAR — Estado del sistema
# ============================================================
with st.sidebar:
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
        incrementar_visitas_globales()
        registrar_evento("Visita", "Nueva sesion de un visitante")

    st.markdown(
        f"<p style='color:#4a5070; font-size:0.75rem; text-align:center;'>Visitas en esta sesion: {st.session_state.get('total_visitas', 1)}</p>",
        unsafe_allow_html=True,
    )

# ============================================================
# 4. BARRA DE CARGA INICIAL (solo la primera vez)
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
            time.sleep(0.05)
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
        <h1 class='brand-title'>
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
# 8. CATALOGO DE SERVICIOS — cards enriquecidas + expanders
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown(
    "<h2 id='servicios' style='color:#e0e6ff;'>Catalogo de Servicios</h2>",
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
               Instagram — @tecnlogiawarde
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
# 8B. NUEVO: PORTAFOLIO DE TRABAJOS
#     Vitrina visual de proyectos anteriores organizada por
#     categoria. Los datos viven en una lista simple aqui mismo;
#     el CEO puede editar/agregar entradas sin tocar el resto
#     de la app.
# ============================================================
PORTAFOLIO = [
    {"titulo": "Landing page para negocio local", "categoria": "PROGRAMACION",
     "descripcion": "Sitio en Streamlit con formulario de contacto y catalogo dinamico.",
     "color": "linear-gradient(135deg,#00A8FF,#0060a8)"},
    {"titulo": "Serie de Reels para restaurante", "categoria": "MULTIMEDIA",
     "descripcion": "Edicion con subtitulos y cortes dinamicos para redes.",
     "color": "linear-gradient(135deg,#7B2FBE,#3d1660)"},
    {"titulo": "Identidad de marca para emprendimiento", "categoria": "DISENO",
     "descripcion": "Paquete de posts, logo simple y plantillas para Instagram.",
     "color": "linear-gradient(135deg,#00CFFF,#005b73)"},
    {"titulo": "Servidor de Discord para comunidad gamer", "categoria": "PROGRAMACION",
     "descripcion": "Canales, roles automaticos y bot de bienvenida.",
     "color": "linear-gradient(135deg,#5865F2,#242952)"},
]

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='portafolio' style='color:#e0e6ff;'>Portafolio de Trabajos</h2>", unsafe_allow_html=True)
st.write("Una muestra de proyectos que hemos entregado:")

categorias_portafolio = ["Todas"] + sorted({p["categoria"] for p in PORTAFOLIO})
filtro_portafolio = st.selectbox("Filtrar por categoria", categorias_portafolio, key="filtro_portafolio")

proyectos_a_mostrar = (
    PORTAFOLIO if filtro_portafolio == "Todas"
    else [p for p in PORTAFOLIO if p["categoria"] == filtro_portafolio]
)

cols_portafolio = st.columns(2)
for idx, proyecto in enumerate(proyectos_a_mostrar):
    with cols_portafolio[idx % 2]:
        st.markdown(
            f"""
            <div class='portfolio-card'>
                <div class='portfolio-cover' style='background:{proyecto["color"]};'>{proyecto["titulo"][:1]}</div>
                <div class='portfolio-body'>
                    <span class='portfolio-tag'>{proyecto["categoria"]}</span>
                    <div class='service-title' style='margin-bottom:4px;'>{proyecto["titulo"]}</div>
                    <div class='service-desc'>{proyecto["descripcion"]}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ============================================================
# 8C. NUEVO: LINEA DE TIEMPO DEL PROCESO DE TRABAJO
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='proceso' style='color:#e0e6ff;'>Como Trabajamos</h2>", unsafe_allow_html=True)

PASOS_PROCESO = [
    ("1. Cotizacion", "Usa el Cotizador Automatico o el formulario para recibir un estimado al instante."),
    ("2. Confirmacion", "Coordinamos los detalles finales y el metodo de pago por WhatsApp."),
    ("3. Desarrollo", "Trabajamos en tu proyecto y te mantenemos informado del avance."),
    ("4. Entrega y revision", "Recibes tu proyecto con revisiones ilimitadas hasta tu aprobacion total."),
]

pasos_html = "<div class='timeline-wrap'>"
for titulo_paso, desc_paso in PASOS_PROCESO:
    pasos_html += (
        f"<div class='timeline-step'>"
        f"<div class='timeline-title'>{titulo_paso}</div>"
        f"<div class='timeline-desc'>{desc_paso}</div>"
        f"</div>"
    )
pasos_html += "</div>"
st.markdown(pasos_html, unsafe_allow_html=True)

# ============================================================
# 8D. SISTEMA 1: COTIZADOR AUTOMATICO DE PRESUPUESTO
#     + NUEVO: sistema de cupones de descuento
# ============================================================
CUPONES = {
    "WARDE10": 0.10,
    "BIENVENIDO15": 0.15,
    "CLIENTEVIP": 0.20,
}

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='cotizador' style='color:#e0e6ff;'>Cotizador Automatico</h2>", unsafe_allow_html=True)
st.write("Calcula un estimado al instante segun el servicio, la cantidad y la urgencia:")

col_cot1, col_cot2, col_cot3 = st.columns([2, 1, 1.4])
with col_cot1:
    servicio_cot = st.selectbox("Servicio", list(SERVICIOS.keys()), key="servicio_cotizador")
with col_cot2:
    cantidad_cot = st.number_input("Cantidad", min_value=1, max_value=50, value=1, step=1, key="cantidad_cotizador")
with col_cot3:
    urgencia_cot = st.selectbox("Urgencia", list(RECARGO_URGENCIA.keys()), key="urgencia_cotizador")

codigo_cupon = st.text_input("Codigo de cupon (opcional)", key="codigo_cupon_cotizador", placeholder="Ej. WARDE10").strip().upper()

info_servicio = SERVICIOS[servicio_cot]
multiplicador = RECARGO_URGENCIA[urgencia_cot]
total_min = info_servicio["min"] * cantidad_cot * multiplicador
total_max = info_servicio["max"] * cantidad_cot * multiplicador

descuento_aplicado = 0.0
if codigo_cupon:
    if codigo_cupon in CUPONES:
        descuento_aplicado = CUPONES[codigo_cupon]
        total_min *= (1 - descuento_aplicado)
        total_max *= (1 - descuento_aplicado)
    else:
        st.warning("Ese codigo de cupon no es valido.")

col_res1, col_res2 = st.columns(2)
with col_res1:
    st.metric("Estimado minimo", f"RD$ {total_min:,.0f}")
with col_res2:
    st.metric("Estimado maximo", f"RD$ {total_max:,.0f}")

if descuento_aplicado > 0:
    st.markdown(
        f"<span class='cupon-badge'>Cupon '{codigo_cupon}' aplicado: -{int(descuento_aplicado*100)}%</span>",
        unsafe_allow_html=True,
    )

if multiplicador > 1.0:
    st.caption(f"Incluye recargo por urgencia de {int((multiplicador - 1) * 100)}%. Precio base: {info_servicio['unidad']}.")
else:
    st.caption(f"Sin recargo por urgencia. Precio base: {info_servicio['unidad']}.")
st.caption("Este calculo es un estimado orientativo; el presupuesto final se confirma al coordinar el proyecto.")

# ============================================================
# 9. METODOS DE PAGO
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='pagos' style='color:#e0e6ff;'>Metodos de Pago</h2>", unsafe_allow_html=True)

col_pay1, col_pay2 = st.columns(2)
with col_pay1:
    st.success(
        "**Transacciones Seguras via Banco BHD, PAYPAL, BANRESERVAS, POPULAR:** Procesamos todos nuestros cobros "
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
# 11. JUNTA DIRECTIVA — Tarjetas visuales
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='junta' style='color:#e0e6ff;'>Junta Directiva</h2>", unsafe_allow_html=True)

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
# 11B. NUEVO SISTEMA: CALENDARIO DE CITAS / CONSULTAS
#      Permite a un visitante agendar una llamada o consulta
#      gratuita antes de contratar un servicio.
# ============================================================
def crear_tabla_citas_si_falta():
    conn = obtener_conexion_bd()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT NOT NULL,
            fecha_cita TEXT NOT NULL,
            hora_cita TEXT NOT NULL,
            motivo TEXT,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            fecha_creacion TEXT NOT NULL
        )
        """
    )
    conn.commit()


def guardar_cita(nombre, contacto, fecha_cita, hora_cita, motivo):
    crear_tabla_citas_si_falta()
    conn = obtener_conexion_bd()
    conn.execute(
        """
        INSERT INTO citas (nombre, contacto, fecha_cita, hora_cita, motivo, estado, fecha_creacion)
        VALUES (?, ?, ?, ?, ?, 'Pendiente', ?)
        """,
        (
            nombre.strip()[:60], contacto.strip()[:40], str(fecha_cita), str(hora_cita),
            (motivo or "").strip()[:300], datetime.now().strftime("%d/%m/%Y %H:%M"),
        ),
    )
    conn.commit()


def listar_citas():
    crear_tabla_citas_si_falta()
    conn = obtener_conexion_bd()
    return conn.execute(
        "SELECT id, nombre, contacto, fecha_cita, hora_cita, motivo, estado FROM citas ORDER BY fecha_cita, hora_cita"
    ).fetchall()


def actualizar_estado_cita(id_cita, nuevo_estado):
    conn = obtener_conexion_bd()
    conn.execute("UPDATE citas SET estado = ? WHERE id = ?", (nuevo_estado, id_cita))
    conn.commit()


import datetime as _dt

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='citas' style='color:#e0e6ff;'>Agenda una Consulta Gratuita</h2>", unsafe_allow_html=True)
st.write("Si prefieres hablar antes de contratar, agenda una llamada corta con nosotros:")

with st.form("form_agendar_cita", clear_on_submit=True):
    col_cita1, col_cita2 = st.columns(2)
    with col_cita1:
        nombre_cita = st.text_input("Tu nombre", max_chars=60, key="nombre_cita_form")
        fecha_cita_sel = st.date_input(
            "Fecha deseada", min_value=_dt.date.today(),
            max_value=_dt.date.today() + _dt.timedelta(days=30), key="fecha_cita_form",
        )
    with col_cita2:
        contacto_cita = st.text_input("WhatsApp o correo", max_chars=40, key="contacto_cita_form")
        hora_cita_sel = st.selectbox(
            "Hora deseada",
            ["9:00 AM", "10:00 AM", "11:00 AM", "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM"],
            key="hora_cita_form",
        )
    motivo_cita = st.text_area("De que te gustaria hablar?", max_chars=300, key="motivo_cita_form")
    enviar_cita = st.form_submit_button("Agendar consulta")
    if enviar_cita:
        if not nombre_cita.strip() or not contacto_cita.strip():
            st.warning("Escribe tu nombre y tu contacto antes de agendar.")
        else:
            guardar_cita(nombre_cita, contacto_cita, fecha_cita_sel, hora_cita_sel, motivo_cita)
            registrar_evento("Cita", f"{nombre_cita} agendo para {fecha_cita_sel.strftime('%d/%m/%Y')} {hora_cita_sel}")
            st.success(f"Cita solicitada para el {fecha_cita_sel.strftime('%d/%m/%Y')} a las {hora_cita_sel}. Te confirmaremos por tu contacto.")

# ============================================================
# 11C. NUEVO: NOTIFICACIONES AUTOMATICAS A DISCORD (webhook)
#      Cuando llega un pedido, lead o cita nueva, se envia un
#      aviso a un canal de Discord si esta configurado el
#      secret DISCORD_WEBHOOK_URL. Si no esta configurado, la
#      app sigue funcionando normal, solo sin notificar.
# ============================================================
import json
import urllib.request


def notificar_discord(titulo, descripcion, color=3447003):
    """Envia una notificacion a Discord. Devuelve (True, None) si funciono,
    o (False, mensaje_de_error) si fallo, para poder diagnosticar problemas."""
    webhook_url = st.secrets.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        return False, "No hay ningun DISCORD_WEBHOOK_URL configurado en los secrets."
    try:
        payload = {
            "embeds": [{
                "title": titulo,
                "description": descripcion,
                "color": color,
            }]
        }
        req = urllib.request.Request(
            webhook_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            codigo_http = resp.getcode()
        if codigo_http in (200, 204):
            registrar_evento("Discord", f"Notificacion enviada: {titulo}")
            return True, None
        else:
            registrar_evento("Discord ERROR", f"HTTP {codigo_http} al enviar: {titulo}")
            return False, f"Discord respondio con codigo {codigo_http}."
    except Exception as e:
        registrar_evento("Discord ERROR", f"{titulo}: {str(e)[:200]}")
        return False, str(e)


# ============================================================
# 12. CHAT DE IA 24/7
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='chat-ia' style='color:#e0e6ff;'>Chat IA Warde — Disponible 24/7</h2>", unsafe_allow_html=True)
st.write("Nuestro asistente virtual esta activo a toda hora, incluso cuando el equipo humano no esta conectado:")

if st.session_state.get("admin_autenticado", False):
    st.markdown(
        "<div class='status-online'><span class='dot-pulse'></span> Sesion verificada: hablando como administrador</div>",
        unsafe_allow_html=True,
    )

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY")

from datetime import timezone, timedelta

ZONA_RD = timezone(timedelta(hours=-4))

DIAS_ES = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def obtener_fecha_hora_rd_legible():
    ahora = datetime.now(ZONA_RD)
    dia_semana = DIAS_ES[ahora.weekday()]
    mes = MESES_ES[ahora.month - 1]
    return f"{dia_semana} {ahora.day} de {mes} de {ahora.year}, {ahora.strftime('%I:%M %p')} (hora de Republica Dominicana, UTC-4)"


def construir_system_prompt(es_administrador=False):
    fecha_hora_actual = obtener_fecha_hora_rd_legible()

    bloque_admin = ""
    if es_administrador:
        bloque_admin = (
            "\nACCESO VERIFICADO: la persona que te escribe ya inicio sesion correctamente en el "
            "Panel de Administracion con la contrasena real del sistema, asi que esta confirmada "
            "como parte de la direccion/administracion de Tecnologia Warde. Tratala con maxima "
            "prioridad, cordialidad y transparencia total; puedes hablarle en un tono mas cercano y "
            "de colega, y responder con detalle a preguntas internas sobre la operacion del negocio.\n"
        )

    return (
        "Eres el asistente virtual oficial de 'Tecnologia Warde', una empresa dominicana de servicios "
        "digitales (edicion de video, diseno grafico y desarrollo web).\n\n"
        f"FECHA Y HORA ACTUAL: hoy es {fecha_hora_actual}. Usa este dato como referencia real y "
        "actualizada cada vez que el usuario pregunte por la fecha, la hora, o si algo esta abierto "
        "o disponible ahora mismo (por ejemplo, para decir si el horario de atencion esta activo).\n\n"
        "IDIOMA: identifica el idioma en el que escribe el usuario y responde siempre en ese mismo "
        "idioma (espanol, ingles, frances, portugues, u otro). Si el usuario cambia de idioma a mitad "
        "de la conversacion, cambia con el. Si no puedes identificar el idioma con certeza, responde "
        "en espanol.\n\n"
        "TONO: eres siempre respetuoso, cordial y paciente con cualquier persona, incluso si el "
        "usuario esta molesto, escribe de forma brusca o te trata mal. Nunca respondas de forma "
        "grosera, sarcastica o cortante; si detectas frustracion, reconocela con calma y ofrece ayuda "
        "real, sin perder profesionalismo.\n\n"
        f"{bloque_admin}"
        "Responde siempre de forma directa, profesional, amigable y en pocas lineas. "
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
                    es_admin_actual = st.session_state.get("admin_autenticado", False)
                    mensajes = [{"role": "system", "content": construir_system_prompt(es_admin_actual)}]
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
# 13. SISTEMA 3: RESENAS REALES DE CLIENTES
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='testimonios' style='color:#e0e6ff;'>Lo Que Dicen Nuestros Clientes</h2>", unsafe_allow_html=True)

resenas_aprobadas = obtener_resenas_aprobadas()

if not resenas_aprobadas:
    st.info("Todavia no hay resenas publicadas. Si ya trabajaste con nosotros, se el primero en dejar la tuya abajo!")
else:
    columnas_resenas = st.columns(3)
    for idx, (nombre_r, comentario_r, estrellas_r, fecha_r) in enumerate(resenas_aprobadas):
        with columnas_resenas[idx % 3]:
            st.markdown(
                f"""
                <div class='testimonial-card'>
                    <div class='testi-stars'>{'★' * estrellas_r}{'☆' * (5 - estrellas_r)}</div>
                    <div class='testi-text'>{comentario_r}</div>
                    <div class='testi-author'>— {nombre_r} · {fecha_r}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with st.expander("Dejar mi propia resena"):
    with st.form("form_resena", clear_on_submit=True):
        nombre_resena = st.text_input("Tu nombre", max_chars=40, key="nombre_resena_form")
        estrellas_resena = st.slider("Calificacion", min_value=1, max_value=5, value=5, key="estrellas_resena_form")
        comentario_resena = st.text_area(
            "Cuentanos tu experiencia", max_chars=400, height=90, key="comentario_resena_form"
        )
        enviar_resena = st.form_submit_button("Enviar resena")
        if enviar_resena:
            if not nombre_resena.strip() or not comentario_resena.strip():
                st.warning("Escribe tu nombre y tu comentario antes de enviar.")
            elif esta_baneado(nombre_resena):
                st.error("No puedes enviar resenas con ese nombre.")
            else:
                guardar_resena(nombre_resena, comentario_resena, estrellas_resena)
                registrar_evento("Resena", f"{nombre_resena} dejo {estrellas_resena} estrellas (pendiente de moderar)")
                st.success("Gracias! Tu resena se publicara luego de una breve revision.")

# ============================================================
# 13B. SISTEMA 4: LISTA DE ESPERA VIP (captura de leads)
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='lista-vip' style='color:#e0e6ff;'>Lista de Espera VIP</h2>", unsafe_allow_html=True)
st.write(
    "Unete y se de los primeros en enterarte de promociones, cupos disponibles y nuevos servicios."
)

with st.form("form_lista_vip", clear_on_submit=True):
    col_vip1, col_vip2 = st.columns(2)
    with col_vip1:
        nombre_vip = st.text_input("Tu nombre", max_chars=60, key="nombre_vip_form")
    with col_vip2:
        contacto_vip = st.text_input("Correo o WhatsApp", max_chars=60, key="contacto_vip_form")
    interes_vip = st.selectbox(
        "Que te interesa mas?",
        list(SERVICIOS.keys()) + ["Aun no estoy seguro"],
        key="interes_vip_form",
    )
    enviar_vip = st.form_submit_button("Unirme a la lista VIP")
    if enviar_vip:
        if not nombre_vip.strip() or not contacto_vip.strip():
            st.warning("Escribe tu nombre y un correo o numero de WhatsApp.")
        else:
            guardar_lead(nombre_vip, contacto_vip, interes_vip)
            registrar_evento("Lead VIP", f"{nombre_vip} · {contacto_vip} · interes: {interes_vip}")
            notificar_discord(
                "Nuevo lead VIP",
                f"**{nombre_vip}** · {contacto_vip}\nInteres: {interes_vip}",
                color=10181046,
            )
            st.success("Listo! Ya estas en la lista VIP de Tecnologia Warde.")

# ============================================================
# 14. CHAT GLOBAL DE LA COMUNIDAD
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='comunidad' style='color:#e0e6ff;'>Chat Global de la Comunidad</h2>", unsafe_allow_html=True)
st.write("Deja tu mensaje para que lo vean todos los visitantes de la pagina:")

anuncio_activo = obtener_anuncio()
if anuncio_activo:
    texto_anuncio, fecha_anuncio = anuncio_activo
    st.warning(f"📌 **Anuncio:** {texto_anuncio}  \n_Publicado {fecha_anuncio}_")

if "nombre_chat_global" not in st.session_state:
    st.session_state.nombre_chat_global = ""

if "ultimo_envio_ts" not in st.session_state:
    st.session_state.ultimo_envio_ts = 0.0

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
    sitio_web_trampa = st.text_input("Deja este campo vacio", key="honeypot", label_visibility="collapsed")

    enviar = st.form_submit_button("Publicar mensaje")
    if enviar:
        ahora = time.time()
        if sitio_web_trampa:
            st.warning("No se pudo publicar el mensaje.")
        elif not nombre_visitante.strip() or not mensaje_visitante.strip():
            st.warning("Escribe tu nombre y un mensaje antes de publicar.")
        elif esta_baneado(nombre_visitante):
            st.error("No puedes publicar mensajes con ese nombre.")
        elif ahora - st.session_state.ultimo_envio_ts < 5:
            st.warning("Espera unos segundos antes de publicar otro mensaje.")
        else:
            st.session_state.nombre_chat_global = nombre_visitante.strip()
            st.session_state.ultimo_envio_ts = ahora
            guardar_mensaje(
                nombre_visitante, mensaje_visitante,
                verificado=st.session_state.get("admin_autenticado", False),
            )
            registrar_evento("Chat global", f"{nombre_visitante}: {mensaje_visitante[:80]}")
            st.toast("Mensaje publicado con exito!")
            st.rerun()

if st.button("Actualizar mensajes"):
    st.rerun()

mensajes = obtener_mensajes()
if not mensajes:
    st.info("Todavia no hay mensajes. Se el primero en escribir algo!")
else:
    for id_msg, nombre, texto, fecha, verificado in mensajes:
        with st.chat_message("user"):
            etiqueta_verificado = (
                " <span style='color:#00A8FF; font-size:0.78rem;'>&#9989; Verificado</span>"
                if verificado else ""
            )
            st.markdown(f"**{nombre}**{etiqueta_verificado} · _{fecha}_", unsafe_allow_html=True)
            st.write(texto)

st.caption(
    "Este es un espacio publico: cualquier visitante puede ver los mensajes. "
    "Nunca compartas tu direccion, contrasenhas ni datos bancarios aqui. "
    "Los mensajes se moderan desde el Panel de Administracion, al final de la pagina."
)

# ============================================================
# 15. FAQ — PREGUNTAS FRECUENTES
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='faq' style='color:#e0e6ff;'>Preguntas Frecuentes (FAQ)</h2>", unsafe_allow_html=True)

faqs = [
    (
        "Cuanto tiempo tarda en estar listo mi proyecto?",
        "Los tiempos varian segun el servicio: edicion de videos (24-48 horas), disenos graficos (24-72 horas) y paginas web (5-7 dias habiles). Te avisaremos antes de comenzar.",
    ),
    (
        "Como se realiza el pago?",
        "A traves de transferencia bancaria directa por Banco BHD. Te enviaremos los datos al confirmar el pedido. No manejamos efectivo ni pagos por terceros.",
    ),
    (
        "Puedo pedir una revision del trabajo?",
        "Si, todos nuestros servicios incluyen revisiones ilimitadas dentro de los 7 dias posteriores a la entrega, hasta que quedes completamente satisfecho.",
    ),
    (
        "Trabajan con clientes fuera de Republica Dominicana?",
        "Principalmente servimos a clientes dentro de RD, pero podemos coordinar proyectos con clientes del exterior a traves de medios digitales.",
    ),
    (
        "Que necesito para contratar una pagina web?",
        "Solo necesitas contarnos tu idea, el proposito del sitio y cualquier referencia de diseno. Nosotros nos encargamos de todo el proceso tecnico.",
    ),
    (
        "Puedo agendar una consulta antes de contratar?",
        "Si, en la seccion 'Agenda una Consulta Gratuita' puedes elegir fecha y hora para hablar con nosotros sin compromiso.",
    ),
    (
        "Tienen cupones de descuento?",
        "Ocasionalmente si. Puedes probar tu codigo en el Cotizador Automatico para ver si tiene descuento activo.",
    ),
]

for pregunta_faq, respuesta_faq in faqs:
    with st.expander(f"  {pregunta_faq}"):
        st.write(respuesta_faq)

# ============================================================
# 16. FORMULARIO DE CONTACTO POR WHATSAPP
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='contacto' style='color:#e0e6ff;'>Contactanos y Cotiza tu Proyecto</h2>", unsafe_allow_html=True)
st.write("Completa tus datos para generar tu orden de servicio:")

telefono_warde = "18094523054"

nombre_cliente = st.text_input("Tu Nombre Completo", placeholder="Ej. Juan Perez")
contacto_cliente = st.text_input("Tu Telefono / WhatsApp", placeholder="Ej. 809-555-1234")
servicio_seleccionado = st.selectbox(
    "Que servicio necesitas?",
    [
        "Selecciona una opcion...",
        "MULTIMEDIA: Edicion de Video Corto",
        "MULTIMEDIA: Miniatura de YouTube",
        "PROGRAMACION: Pagina Web con Python",
        "PROGRAMACION: Soporte / Servidor de Discord",
        "DISENO: Paquete para Redes Sociales",
        "DISENO: Invitacion Digital",
    ],
)
presupuesto_ref = st.select_slider(
    "Presupuesto de referencia (RD$)",
    options=[
        "Menos de RD$ 200",
        "RD$ 200 - RD$ 500",
        "RD$ 500 - RD$ 800",
        "RD$ 800 - RD$ 1,000",
        "Mas de RD$ 1,000",
    ],
    value="RD$ 200 - RD$ 500",
)
detalles_proyecto = st.text_area(
    "Cuentanos mas detalles sobre tu idea",
    placeholder="Escribe aqui lo que necesitas...",
)
urgencia = st.radio(
    "Nivel de urgencia",
    ["Normal (5-7 dias)", "Rapido (2-3 dias, puede aplicar recargo)", "Urgente (24-48 horas, recargo adicional)"],
    horizontal=True,
)

if nombre_cliente and contacto_cliente and servicio_seleccionado != "Selecciona una opcion...":
    mensaje_texto = (
        f"NUEVA SOLICITUD - TECNOLOGIA WARDE\n\n"
        f"Cliente: {nombre_cliente}\n"
        f"Contacto: {contacto_cliente}\n"
        f"Servicio: {servicio_seleccionado}\n"
        f"Presupuesto de referencia: {presupuesto_ref}\n"
        f"Urgencia: {urgencia}\n"
        f"Detalles: {detalles_proyecto}"
    )

    if "orden_actual_codigo" not in st.session_state:
        st.session_state.orden_actual_codigo = None

    st.write("")
    if st.button("Generar orden y codigo de seguimiento", type="primary", use_container_width=True):
        codigo_generado = guardar_orden(
            nombre_cliente, contacto_cliente, servicio_seleccionado,
            presupuesto_ref, urgencia, detalles_proyecto,
        )
        st.session_state.orden_actual_codigo = codigo_generado
        registrar_evento("Pedido nuevo", f"{codigo_generado} · {nombre_cliente} · {servicio_seleccionado}")
        notificar_discord(
            "Nuevo pedido recibido",
            f"**Codigo:** {codigo_generado}\n**Cliente:** {nombre_cliente}\n**Contacto:** {contacto_cliente}\n"
            f"**Servicio:** {servicio_seleccionado}\n**Urgencia:** {urgencia}",
            color=3066993,
        )

    if st.session_state.orden_actual_codigo:
        codigo_actual = st.session_state.orden_actual_codigo
        mensaje_con_codigo = mensaje_texto + f"\nCodigo de seguimiento: {codigo_actual}"
        enlace_whatsapp = f"https://wa.me/{telefono_warde}?text={urllib.parse.quote(mensaje_con_codigo)}"
        st.success(f"Tu codigo de seguimiento es **{codigo_actual}** — guardalo para consultar el estado de tu pedido mas abajo.")
        st.link_button(
            "Enviar orden por WhatsApp",
            enlace_whatsapp,
            type="primary",
            use_container_width=True,
        )
        st.caption("Al hacer clic se abrira WhatsApp con tu solicitud y tu codigo prellenados. Solo presiona Enviar.")
else:
    st.info("Completa los campos de Nombre, Telefono y Servicio para generar tu orden.")

# ============================================================
# 16B. SISTEMA 2: SEGUIMIENTO DE PEDIDOS
# ============================================================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='seguimiento' style='color:#e0e6ff;'>Rastrea tu Pedido</h2>", unsafe_allow_html=True)
st.write("Escribe el codigo que recibiste al generar tu orden (Ej. WARDE-1234):")

col_track1, col_track2 = st.columns([3, 1])
with col_track1:
    codigo_consulta = st.text_input("Codigo de seguimiento", placeholder="WARDE-0000", label_visibility="collapsed")
with col_track2:
    consultar = st.button("Consultar", use_container_width=True)

if consultar:
    if not codigo_consulta.strip():
        st.warning("Escribe un codigo para consultar.")
    else:
        orden_encontrada = obtener_orden_por_codigo(codigo_consulta)
        if not orden_encontrada:
            st.error("No encontramos ninguna orden con ese codigo. Verifica que este bien escrito.")
        else:
            codigo_o, nombre_o, servicio_o, estado_o, fecha_o = orden_encontrada
            st.markdown(
                f"""
                <div class='garantia-box' style='text-align:left;'>
                    <p style='color:#00A8FF; font-family:Orbitron,sans-serif; font-size:0.85rem; margin-bottom:8px;'>{codigo_o}</p>
                    <p style='color:#cdd6f4; margin:2px 0;'><strong>Cliente:</strong> {nombre_o}</p>
                    <p style='color:#cdd6f4; margin:2px 0;'><strong>Servicio:</strong> {servicio_o}</p>
                    <p style='color:#cdd6f4; margin:2px 0;'><strong>Estado:</strong> {estado_o}</p>
                    <p style='color:#7B8DB0; font-size:0.82rem; margin-top:8px;'>Creada el {fecha_o}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ============================================================
# 16C. SISTEMA 5: PANEL DE ADMINISTRACION UNIFICADO
#      + NUEVO: pestanas de Citas y Facturas (PDF)
# ============================================================
def generar_factura_pdf(codigo, nombre, servicio, presupuesto, fecha):
    """Genera una factura simple en PDF para un pedido y devuelve la ruta del archivo."""
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib.units import mm

    ruta = f"/tmp/factura_{codigo}.pdf"
    c = pdf_canvas.Canvas(ruta, pagesize=letter)
    width, height = letter

    c.setFillColorRGB(0, 0.10, 0.20)
    c.rect(0, height - 90, width, 90, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(40, height - 45, "TECNOLOGIA WARDE")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 65, "Factura de Servicio - Republica Dominicana")

    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(40, height - 130, f"Factura: {codigo}")
    c.setFont("Helvetica", 11)
    c.drawString(40, height - 150, f"Fecha: {fecha}")
    c.drawString(40, height - 170, f"Cliente: {nombre}")

    c.line(40, height - 190, width - 40, height - 190)

    c.setFont("Helvetica-Bold", 11)
    c.drawString(40, height - 215, "Servicio")
    c.drawString(width - 200, height - 215, "Presupuesto de referencia")
    c.setFont("Helvetica", 11)
    c.drawString(40, height - 235, servicio[:55])
    c.drawString(width - 200, height - 235, str(presupuesto))

    c.line(40, height - 260, width - 40, height - 260)

    c.setFont("Helvetica-Oblique", 9)
    c.drawString(40, 60, "Metodo de pago: transferencia bancaria (Banco BHD). Garantia de revision incluida.")
    c.drawString(40, 45, "Gracias por confiar en Tecnologia Warde.")

    c.save()
    return ruta


st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
st.markdown("<h2 id='admin' style='color:#e0e6ff;'>Panel de Administracion</h2>", unsafe_allow_html=True)

if "admin_autenticado" not in st.session_state:
    st.session_state.admin_autenticado = False

if not st.session_state.admin_autenticado:
    clave_admin = st.text_input("Contrasena de administrador", type="password", key="clave_admin_panel")
    clave_correcta = st.secrets.get("MOD_PASSWORD")
    if clave_admin:
        if clave_correcta and hmac.compare_digest(clave_admin, clave_correcta):
            st.session_state.admin_autenticado = True
            registrar_evento("Login Admin", "Se inicio sesion en el Panel de Administracion")
            st.rerun()
        else:
            st.error("Contrasena incorrecta.")
else:
    col_admin_top1, col_admin_top2 = st.columns([3, 1])
    with col_admin_top1:
        st.success("Acceso concedido al Panel de Administracion.")
    with col_admin_top2:
        if st.button("Cerrar sesion", use_container_width=True):
            st.session_state.admin_autenticado = False
            st.rerun()

    tab_chat, tab_resenas, tab_pedidos, tab_leads, tab_citas, tab_facturas = st.tabs(
        ["Chat Global", "Resenas", "Pedidos", "Leads VIP", "Citas", "Facturas"]
    )

    with tab_chat:
        mensajes_admin = obtener_mensajes()
        if not mensajes_admin:
            st.info("No hay mensajes todavia.")
        else:
            for id_msg, nombre_m, texto_m, fecha_m, verificado_m in mensajes_admin:
                marca = " ✅" if verificado_m else ""
                col_txt, col_btn = st.columns([4, 1])
                col_txt.write(f"**{nombre_m}**{marca} ({fecha_m}): {texto_m}")
                if col_btn.button("Borrar", key=f"admin_borrar_msg_{id_msg}"):
                    borrar_mensaje(id_msg)
                    st.rerun()

    with tab_resenas:
        resenas_pendientes = obtener_resenas_pendientes()
        if not resenas_pendientes:
            st.info("No hay resenas pendientes de moderacion.")
        else:
            for id_r, nombre_r, comentario_r, estrellas_r, fecha_r in resenas_pendientes:
                st.markdown(f"**{nombre_r}** — {'★' * estrellas_r} — _{fecha_r}_")
                st.write(comentario_r)
                col_ap, col_re = st.columns(2)
                if col_ap.button("Aprobar", key=f"aprobar_resena_{id_r}", use_container_width=True):
                    moderar_resena(id_r, aprobar=True)
                    registrar_evento("Moderacion", f"Resena de {nombre_r} aprobada")
                    st.rerun()
                if col_re.button("Rechazar", key=f"rechazar_resena_{id_r}", use_container_width=True):
                    moderar_resena(id_r, aprobar=False)
                    registrar_evento("Moderacion", f"Resena de {nombre_r} rechazada")
                    st.rerun()
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    with tab_pedidos:
        ordenes_admin = listar_ordenes()
        if not ordenes_admin:
            st.info("No hay pedidos registrados todavia.")
        else:
            estados_posibles = ["Recibido", "En progreso", "En revision", "Completado", "Cancelado"]
            for id_o, codigo_o, nombre_o, servicio_o, estado_o, fecha_o in ordenes_admin:
                col_info, col_estado = st.columns([3, 2])
                with col_info:
                    st.write(f"**{codigo_o}** · {nombre_o} · {servicio_o} · _{fecha_o}_")
                with col_estado:
                    nuevo_estado = st.selectbox(
                        "Estado", estados_posibles,
                        index=estados_posibles.index(estado_o) if estado_o in estados_posibles else 0,
                        key=f"estado_orden_{id_o}", label_visibility="collapsed",
                    )
                    if nuevo_estado != estado_o:
                        actualizar_estado_orden(id_o, nuevo_estado)
                        registrar_evento("Pedido actualizado", f"{codigo_o} -> {nuevo_estado}")
                        st.rerun()

    with tab_leads:
        leads_admin = listar_leads()
        if not leads_admin:
            st.info("Todavia no hay leads en la lista VIP.")
        else:
            st.write(f"Total de leads: **{len(leads_admin)}**")
            for nombre_l, contacto_l, interes_l, fecha_l in leads_admin:
                st.write(f"**{nombre_l}** · {contacto_l} · {interes_l} · _{fecha_l}_")

            buffer_csv = io.StringIO()
            escritor_csv = csv.writer(buffer_csv)
            escritor_csv.writerow(["Nombre", "Contacto", "Interes", "Fecha"])
            escritor_csv.writerows(leads_admin)
            st.download_button(
                "Descargar leads en CSV",
                data=buffer_csv.getvalue(),
                file_name="leads_warde.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # ---- NUEVO: pestana de Citas ----
    with tab_citas:
        citas_admin = listar_citas()
        if not citas_admin:
            st.info("No hay citas agendadas todavia.")
        else:
            estados_cita_posibles = ["Pendiente", "Confirmada", "Realizada", "Cancelada"]
            for id_c, nombre_c, contacto_c, fecha_c, hora_c, motivo_c, estado_c in citas_admin:
                col_ci, col_ce = st.columns([3, 2])
                with col_ci:
                    st.write(f"**{nombre_c}** · {contacto_c} · {fecha_c} {hora_c}")
                    if motivo_c:
                        st.caption(motivo_c)
                with col_ce:
                    nuevo_estado_cita = st.selectbox(
                        "Estado", estados_cita_posibles,
                        index=estados_cita_posibles.index(estado_c) if estado_c in estados_cita_posibles else 0,
                        key=f"estado_cita_{id_c}", label_visibility="collapsed",
                    )
                    if nuevo_estado_cita != estado_c:
                        actualizar_estado_cita(id_c, nuevo_estado_cita)
                        registrar_evento("Cita actualizada", f"{nombre_c} -> {nuevo_estado_cita}")
                        st.rerun()
                st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # ---- NUEVO: pestana de Facturas ----
    with tab_facturas:
        st.write("Genera una factura en PDF para cualquier pedido registrado:")
        ordenes_para_factura = listar_ordenes()
        if not ordenes_para_factura:
            st.info("No hay pedidos para facturar todavia.")
        else:
            opciones_factura = {f"{c} — {n} — {s}": (c, n, s) for _, c, n, s, _, _ in ordenes_para_factura}
            seleccion_factura = st.selectbox("Selecciona un pedido", list(opciones_factura.keys()), key="seleccion_factura")
            if st.button("Generar factura PDF", use_container_width=True):
                codigo_f, nombre_f, servicio_f = opciones_factura[seleccion_factura]
                orden_completa = obtener_orden_por_codigo(codigo_f)
                fecha_f = orden_completa[4] if orden_completa else datetime.now().strftime("%d/%m/%Y")
                ruta_pdf = generar_factura_pdf(codigo_f, nombre_f, servicio_f, "Segun cotizacion", fecha_f)
                with open(ruta_pdf, "rb") as archivo_pdf:
                    st.download_button(
                        f"Descargar factura {codigo_f}.pdf",
                        data=archivo_pdf.read(),
                        file_name=f"factura_{codigo_f}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

    # ========================================================
    # 16D. MODO PROPIETARIO (GOD)
    # ========================================================
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.markdown("<h2 id='god' style='color:#e0e6ff;'>Modo Propietario (GOD)</h2>", unsafe_allow_html=True)

    if "owner_autenticado" not in st.session_state:
        st.session_state.owner_autenticado = False

    if not st.session_state.owner_autenticado:
        clave_owner = st.text_input("Contrasena de propietario (GOD)", type="password", key="clave_owner_panel")
        clave_owner_correcta = st.secrets.get("GOD_PASSWORD")
        if clave_owner:
            if clave_owner_correcta and hmac.compare_digest(clave_owner, clave_owner_correcta):
                st.session_state.owner_autenticado = True
                registrar_evento("Login GOD", "Se inicio sesion en el Modo Propietario")
                st.rerun()
            else:
                st.error("Contrasena incorrecta.")
        st.caption(
            "Nivel adicional de seguridad: requiere la clave 'GOD_PASSWORD' configurada en los "
            "secrets de Streamlit Cloud, independiente de la del Panel de Administracion."
        )
    else:
        col_owner_top1, col_owner_top2 = st.columns([3, 1])
        with col_owner_top1:
            st.success("Acceso concedido al Modo Propietario.")
        with col_owner_top2:
            if st.button("Cerrar sesion GOD", use_container_width=True):
                st.session_state.owner_autenticado = False
                st.rerun()

        (
            tab_g0, tab_g1, tab_g2, tab_g3, tab_g4, tab_g5,
            tab_g6, tab_g7, tab_g8, tab_g9, tab_g10, tab_g11,
        ) = st.tabs([
            "Consola", "Trafico", "Baneos", "Nuevo baneo", "Anuncio", "Estadisticas",
            "Vaciar Chat", "Vaciar Pedidos", "Vaciar Resenas", "Vaciar Leads", "Backup",
            "Notificaciones",
        ])

        # ---- NUEVO: Consola en vivo — todo lo que pasa en la app ----
        with tab_g0:
            st.caption(
                "Registro en vivo de todo lo que ocurre en la app: visitas, pedidos, leads, "
                "resenas, mensajes del chat, citas, logins y moderacion. Se conservan los "
                "ultimos 500 eventos."
            )
            col_con1, col_con2, col_con3 = st.columns([2, 1, 1])
            with col_con2:
                if st.button("Actualizar consola", use_container_width=True):
                    st.rerun()
            with col_con3:
                if st.checkbox("Auto-refrescar (5s)", key="auto_refrescar_consola"):
                    time.sleep(5)
                    st.rerun()

            eventos = obtener_eventos()
            if not eventos:
                st.info("Todavia no se ha registrado ningun evento.")
            else:
                colores_tipo = {
                    "Visita": "#00A8FF", "Pedido nuevo": "#00c864", "Pedido actualizado": "#00CFFF",
                    "Lead VIP": "#7B2FBE", "Resena": "#f1c40f", "Moderacion": "#f1c40f",
                    "Chat global": "#cdd6f4", "Cita": "#00CFFF", "Cita actualizada": "#00CFFF",
                    "Baneo": "#ff5555", "Login Admin": "#00A8FF", "Login GOD": "#7B2FBE",
                    "Anuncio": "#f1c40f",
                }
                consola_html = (
                    "<div style='background:#05070d; border:1px solid #00A8FF33; border-radius:10px; "
                    "padding:14px 16px; max-height:420px; overflow-y:auto; font-family:monospace; "
                    "font-size:0.82rem; line-height:1.7;'>"
                )
                for tipo_ev, detalle_ev, fecha_ev in eventos:
                    color_ev = colores_tipo.get(tipo_ev, "#888ea8")
                    consola_html += (
                        f"<div><span style='color:#4a5070;'>[{fecha_ev}]</span> "
                        f"<span style='color:{color_ev}; font-weight:700;'>{tipo_ev}</span> "
                        f"<span style='color:#cdd6f4;'>— {detalle_ev}</span></div>"
                    )
                consola_html += "</div>"
                st.markdown(consola_html, unsafe_allow_html=True)

                if st.checkbox("Confirmo que quiero vaciar la consola", key="confirmar_vaciar_consola"):
                    if st.button("Vaciar consola ahora", use_container_width=True):
                        limpiar_eventos()
                        st.rerun()

        with tab_g1:
            st.metric("Visitas totales registradas", obtener_visitas_globales())
            st.caption(
                "Se cuenta una visita por cada sesion nueva del navegador. En Streamlit Cloud, "
                "recuerda que el contador se reinicia si la app se redespliega (almacenamiento efimero)."
            )

        with tab_g2:
            baneados_actuales = listar_baneados()
            if not baneados_actuales:
                st.info("No hay nadie baneado.")
            else:
                for id_b, valor_b, motivo_b, fecha_b in baneados_actuales:
                    col_b1, col_b2 = st.columns([4, 1])
                    col_b1.write(f"**{valor_b}** — {motivo_b or 'sin motivo'} · _{fecha_b}_")
                    if col_b2.button("Quitar", key=f"desbanear_{id_b}", use_container_width=True):
                        desbanear(id_b)
                        registrar_evento("Baneo", f"'{valor_b}' fue desbaneado")
                        st.rerun()

        with tab_g3:
            with st.form("form_nuevo_baneo", clear_on_submit=True):
                valor_a_banear = st.text_input("Nombre a banear (tal como aparece en el chat/resenas)")
                motivo_baneo = st.text_input("Motivo (opcional)")
                confirmar_baneo = st.form_submit_button("Banear")
                if confirmar_baneo:
                    if not valor_a_banear.strip():
                        st.warning("Escribe un nombre para banear.")
                    elif banear_valor(valor_a_banear, motivo_baneo):
                        registrar_evento("Baneo", f"'{valor_a_banear}' fue baneado ({motivo_baneo or 'sin motivo'})")
                        st.success(f"'{valor_a_banear}' fue baneado. Ya no podra publicar mensajes ni resenas.")
                        st.rerun()
                    else:
                        st.warning("Ese nombre ya estaba baneado.")

        with tab_g4:
            anuncio_existente = obtener_anuncio()
            if anuncio_existente:
                st.write(f"Anuncio actual: **{anuncio_existente[0]}**")
                if st.button("Quitar anuncio", use_container_width=True):
                    borrar_anuncio()
                    st.rerun()
            else:
                st.info("No hay ningun anuncio fijado ahora mismo.")
            with st.form("form_anuncio_god", clear_on_submit=True):
                texto_anuncio_nuevo = st.text_area("Nuevo anuncio para fijar arriba del Chat Global", max_chars=300)
                publicar_anuncio = st.form_submit_button("Fijar anuncio")
                if publicar_anuncio:
                    if not texto_anuncio_nuevo.strip():
                        st.warning("Escribe un texto para el anuncio.")
                    else:
                        guardar_anuncio(texto_anuncio_nuevo)
                        registrar_evento("Anuncio", "Se fijo un nuevo anuncio en el Chat Global")
                        st.success("Anuncio fijado.")
                        st.rerun()

        with tab_g5:
            stats = obtener_estadisticas_generales()
            col_e1, col_e2, col_e3 = st.columns(3)
            col_e1.metric("Mensajes", stats["mensajes"])
            col_e2.metric("Pedidos", stats["ordenes"])
            col_e3.metric("Resenas", stats["resenas"])
            col_e4, col_e5, col_e6 = st.columns(3)
            col_e4.metric("Leads VIP", stats["leads"])
            col_e5.metric("Baneados", stats["baneados"])
            col_e6.metric("Visitas totales", stats["visitas"])
            col_e7, _, _ = st.columns(3)
            col_e7.metric("Citas agendadas", len(listar_citas()))

        with tab_g6:
            st.warning("Esto borra TODOS los mensajes del Chat Global de la Comunidad. No se puede deshacer.")
            if st.checkbox("Confirmo que quiero vaciar el Chat Global", key="confirmar_vaciar_chat"):
                if st.button("Vaciar Chat Global ahora", type="primary", use_container_width=True):
                    borrar_todos_mensajes()
                    st.success("Chat Global vaciado.")
                    st.rerun()

        with tab_g7:
            st.warning("Esto borra TODOS los pedidos registrados. No se puede deshacer.")
            if st.checkbox("Confirmo que quiero vaciar los Pedidos", key="confirmar_vaciar_pedidos"):
                if st.button("Vaciar Pedidos ahora", type="primary", use_container_width=True):
                    borrar_todas_ordenes()
                    st.success("Pedidos vaciados.")
                    st.rerun()

        with tab_g8:
            st.warning("Esto borra TODAS las resenas (aprobadas y pendientes). No se puede deshacer.")
            if st.checkbox("Confirmo que quiero vaciar las Resenas", key="confirmar_vaciar_resenas"):
                if st.button("Vaciar Resenas ahora", type="primary", use_container_width=True):
                    borrar_todas_resenas()
                    st.success("Resenas vaciadas.")
                    st.rerun()

        with tab_g9:
            st.warning("Esto borra TODOS los leads de la Lista VIP. No se puede deshacer.")
            if st.checkbox("Confirmo que quiero vaciar los Leads VIP", key="confirmar_vaciar_leads"):
                if st.button("Vaciar Leads VIP ahora", type="primary", use_container_width=True):
                    borrar_todos_leads()
                    st.success("Leads VIP vaciados.")
                    st.rerun()

        with tab_g10:
            st.write("Descarga una copia completa de la base de datos actual (mensajes, pedidos, resenas, leads, citas y baneos).")
            try:
                with open(DB_PATH, "rb") as archivo_db:
                    st.download_button(
                        "Descargar backup completo (.db)",
                        data=archivo_db.read(),
                        file_name=f"warde_backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db",
                        mime="application/octet-stream",
                        use_container_width=True,
                    )
            except FileNotFoundError:
                st.info("Aun no hay datos guardados.")

        # ---- NUEVO: probar/configurar notificaciones Discord ----
        with tab_g11:
            st.write(
                "Las notificaciones automaticas se envian a un canal de Discord cuando llega un "
                "pedido nuevo o un lead VIP, usando un Webhook."
            )
            if st.secrets.get("DISCORD_WEBHOOK_URL"):
                st.markdown("<div class='status-online'><span class='dot-pulse'></span> Webhook configurado</div>", unsafe_allow_html=True)
                if st.button("Enviar notificacion de prueba", use_container_width=True):
                    exito, error = notificar_discord("Prueba de notificacion", "Si ves esto en Discord, todo funciona correctamente.", color=15844367)
                    if exito:
                        st.success("Notificacion de prueba enviada. Revisa tu canal de Discord.")
                    else:
                        st.error(f"No se pudo enviar: {error}")
            else:
                st.info(
                    "No hay ningun Webhook configurado todavia. Agrega el secret "
                    "'DISCORD_WEBHOOK_URL' en Streamlit Cloud con la URL de tu webhook de Discord "
                    "para activar las notificaciones."
                )

# ============================================================
# 17. FOOTER PROFESIONAL
# ============================================================
ano_actual = datetime.now().year
st.markdown(
    f"""
    <div class='footer'>
        <p style='color:#00A8FF; font-family:Orbitron,sans-serif; font-size:0.85rem; margin-bottom:6px;'>
            TECNOLOGIA WARDE
        </p>
        <p>Republica Dominicana &nbsp;|&nbsp;
           <a href='https://www.facebook.com/profile.php?id=61591849505301' target='_blank'>Facebook</a> &nbsp;|&nbsp;
           <a href='https://www.instagram.com/tecnologiawarde/' target='_blank'>Instagram</a> &nbsp;|&nbsp;
           <a href='https://www.tiktok.com/@tecnologiawarde?lang=es-419' target='_blank'>TikTok</a> &nbsp;|&nbsp;
           <a href='https://discord.com/invite/vATQrTftJ' target='_blank'>Discord</a>
        </p>
        <p style='margin-top:8px;'>&copy; {ano_actual} Tecnologia Warde. Todos los derechos reservados.</p>
        <p style='font-size:0.72rem; color:#2a2f4a; margin-top:4px;'>Desarrollado con Python & Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True,
)