import streamlit as st
import urllib.parse
import sqlite3
from datetime import datetime
import time
import json
import hashlib
import re
from typing import Optional, Dict, List, Tuple

# Intentamos importar la librería oficial de Groq
try:
    from groq import Groq
except ImportError:
    st.error("Falta instalar la librería de Groq. Asegúrate de añadir 'groq' en tu archivo requirements.txt de GitHub.")
    st.stop()

# ============================================================
# 1. CONFIGURACIÓN AVANZADA DE PÁGINA
# ============================================================
st.set_page_config(
    page_title="Tecnología Warde | Innovación Digital RD",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://wa.me/18094523054',
        'Report a bug': "mailto:soporte@tecnologiawarde.com",
        'About': """
        ### Tecnología Warde
        **Innovación Digital para el Futuro**
        
        Transformamos ideas en soluciones tecnológicas de vanguardia.
        
        *Fundada en 2024*
        *República Dominicana*
        """
    }
)

# ============================================================
# 2. SISTEMA DE ESTADO Y CACHE AVANZADO
# ============================================================
class AppState:
    """Gestor de estado de la aplicación con persistencia"""
    
    @staticmethod
    def init_state():
        if "app_initialized" not in st.session_state:
            st.session_state.app_initialized = True
            st.session_state.theme_mode = "dark"
            st.session_state.notifications = []
            st.session_state.user_preferences = {
                "language": "es",
                "notifications": True,
                "compact_mode": False
            }
            st.session_state.analytics = {
                "page_views": 0,
                "chat_interactions": 0,
                "contact_requests": 0
            }
            st.session_state.chat_historial = []
            st.session_state.nombre_chat_global = ""
            st.session_state.visit_count = 0
            
    @staticmethod
    def add_notification(message: str, type: str = "info"):
        st.session_state.notifications.append({
            "message": message,
            "type": type,
            "timestamp": datetime.now().isoformat()
        })
        
    @staticmethod
    def get_notifications():
        return st.session_state.notifications[-5:]  # Últimas 5 notificaciones

# Inicializar estado
AppState.init_state()

# ============================================================
# 3. CSS ULTRA MODERNO - NEUMORFISMO + GLASS + ANIMACIONES
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;600;700&display=swap');
    
    /* ---- Variables Globales ---- */
    :root {
        --primary: #00D4FF;
        --secondary: #7B2FBE;
        --accent: #FF6B6B;
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
        --shadow-dark: rgba(0, 0, 0, 0.3);
        --shadow-glow: rgba(0, 212, 255, 0.15);
        --radius-lg: 24px;
        --radius-md: 16px;
        --radius-sm: 12px;
    }
    
    /* ---- Reset y Fondo ---- */
    .stApp {
        background: #0A0E1A;
        font-family: 'Inter', sans-serif;
        position: relative;
        overflow-x: hidden;
    }
    
    /* ---- Fondo con Partículas Animadas ---- */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(ellipse at 20% 50%, rgba(0, 212, 255, 0.03) 0%, transparent 70%),
            radial-gradient(ellipse at 80% 50%, rgba(123, 47, 190, 0.03) 0%, transparent 70%);
        pointer-events: none;
        z-index: 0;
        animation: floatBackground 20s ease-in-out infinite;
    }
    
    @keyframes floatBackground {
        0%, 100% { transform: scale(1) rotate(0deg); }
        50% { transform: scale(1.05) rotate(1deg); }
    }
    
    /* ---- Grid de Fondo ---- */
    .bg-grid {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
        z-index: 0;
        animation: gridPulse 10s linear infinite;
    }
    
    @keyframes gridPulse {
        0% { opacity: 0.5; }
        50% { opacity: 1; }
        100% { opacity: 0.5; }
    }
    
    /* ---- Sidebar Premium ---- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(10, 14, 26, 0.95), rgba(20, 24, 40, 0.95));
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 4px 0 30px rgba(0, 0, 0, 0.3);
        z-index: 10;
    }
    
    /* ---- Neumorphic Cards ---- */
    .neo-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: var(--radius-md);
        padding: 24px;
        position: relative;
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.1),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-bottom: 16px;
    }
    
    .neo-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, 
            rgba(0, 212, 255, 0.05) 0%,
            rgba(123, 47, 190, 0.05) 100%
        );
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .neo-card:hover {
        transform: translateY(-4px) scale(1.01);
        border-color: rgba(0, 212, 255, 0.2);
        box-shadow: 
            0 12px 48px rgba(0, 0, 0, 0.2),
            0 0 40px rgba(0, 212, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
    }
    
    .neo-card:hover::before {
        opacity: 1;
    }
    
    /* ---- Glow Buttons ---- */
    .glow-btn {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        border: none;
        padding: 12px 32px;
        border-radius: 50px;
        color: white;
        font-weight: 600;
        font-size: 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.3);
        position: relative;
        overflow: hidden;
        text-decoration: none;
        display: inline-block;
    }
    
    .glow-btn::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.2) 0%, transparent 60%);
        opacity: 0;
        transition: opacity 0.3s ease;
        transform: scale(0);
    }
    
    .glow-btn:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.4);
    }
    
    .glow-btn:hover::before {
        opacity: 1;
        transform: scale(1);
    }
    
    /* ---- Service Cards Premium ---- */
    .service-premium {
        background: rgba(255, 255, 255, 0.03);
        border-radius: var(--radius-sm);
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.06);
        transition: all 0.4s ease;
        position: relative;
        overflow: hidden;
        margin-bottom: 12px;
        cursor: pointer;
    }
    
    .service-premium::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--primary), var(--secondary));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .service-premium:hover {
        transform: translateX(8px);
        background: rgba(255, 255, 255, 0.06);
        border-color: rgba(0, 212, 255, 0.2);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    }
    
    .service-premium:hover::after {
        opacity: 1;
    }
    
    .service-title-premium {
        color: var(--primary);
        font-family: 'Orbitron', sans-serif;
        font-size: 0.9rem;
        font-weight: 700;
        margin-bottom: 6px;
        letter-spacing: 1px;
    }
    
    .service-desc-premium {
        color: #B0C4DE;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    
    .service-badge {
        display: inline-block;
        padding: 4px 12px;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(123, 47, 190, 0.2));
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 20px;
        color: var(--primary);
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 8px;
    }
    
    /* ---- Founder Cards Avanzadas ---- */
    .founder-premium {
        background: rgba(255, 255, 255, 0.03);
        border-radius: var(--radius-md);
        padding: 24px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .founder-premium::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.05) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .founder-premium:hover {
        transform: translateY(-8px) scale(1.02);
        border-color: rgba(0, 212, 255, 0.2);
        box-shadow: 
            0 12px 40px rgba(0, 0, 0, 0.3),
            0 0 60px rgba(0, 212, 255, 0.05);
    }
    
    .founder-premium:hover::before {
        opacity: 1;
    }
    
    .founder-avatar-premium {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 16px;
        font-size: 32px;
        font-weight: 700;
        color: white;
        position: relative;
        box-shadow: 0 4px 20px rgba(0, 212, 255, 0.2);
    }
    
    .founder-avatar-premium::after {
        content: '';
        position: absolute;
        inset: -3px;
        border-radius: 50%;
        padding: 2px;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
    }
    
    /* ---- Estadísticas Animadas ---- */
    .stat-premium {
        background: rgba(255, 255, 255, 0.03);
        border-radius: var(--radius-sm);
        padding: 20px;
        text-align: center;
        border: 1px solid rgba(255, 255, 255, 0.05);
        transition: all 0.3s ease;
    }
    
    .stat-premium:hover {
        transform: scale(1.05);
        border-color: rgba(0, 212, 255, 0.2);
        box-shadow: 0 8px 24px rgba(0, 212, 255, 0.1);
    }
    
    .stat-number-premium {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.4rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        display: inline-block;
    }
    
    /* ---- Chat Bubbles Modernas ---- */
    .chat-bubble-user {
        background: linear-gradient(135deg, var(--primary), var(--secondary));
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 80%;
        margin: 8px 0;
        box-shadow: 0 4px 12px rgba(0, 212, 255, 0.2);
    }
    
    .chat-bubble-assistant {
        background: rgba(255, 255, 255, 0.06);
        color: #E0E6FF;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        max-width: 80%;
        margin: 8px 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* ---- Testimonios Premium ---- */
    .testimonial-premium {
        background: rgba(255, 255, 255, 0.03);
        border-radius: var(--radius-sm);
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.05);
        position: relative;
        margin-bottom: 12px;
        transition: all 0.3s ease;
    }
    
    .testimonial-premium::before {
        content: '"';
        position: absolute;
        top: -10px;
        left: 16px;
        font-size: 4rem;
        color: rgba(0, 212, 255, 0.1);
        font-family: serif;
    }
    
    .testimonial-premium:hover {
        border-color: rgba(0, 212, 255, 0.15);
        transform: translateX(4px);
    }
    
    /* ---- Garantía Premium ---- */
    .garantia-premium {
        background: linear-gradient(135deg, 
            rgba(0, 212, 255, 0.05),
            rgba(123, 47, 190, 0.05)
        );
        border-radius: var(--radius-md);
        padding: 32px;
        text-align: center;
        border: 1px solid rgba(0, 212, 255, 0.1);
        position: relative;
        overflow: hidden;
        margin: 16px 0;
    }
    
    .garantia-premium::before {
        content: '✦';
        position: absolute;
        font-size: 8rem;
        opacity: 0.03;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        animation: rotateSymbol 20s linear infinite;
    }
    
    @keyframes rotateSymbol {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
    
    /* ---- Glitch Text Effect ---- */
    .glitch-text {
        font-family: 'Orbitron', sans-serif;
        font-size: 2.8rem;
        font-weight: 900;
        background: linear-gradient(135deg, var(--primary), var(--secondary), var(--primary));
        background-size: 200% 200%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 3s ease-in-out infinite;
        position: relative;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ---- Social Links Premium ---- */
    .social-premium {
        display: inline-flex;
        align-items: center;
        gap: 12px;
        padding: 10px 20px;
        border-radius: 50px;
        margin: 4px;
        text-decoration: none;
        color: white !important;
        font-weight: 600;
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    .social-premium:hover {
        transform: translateY(-4px) scale(1.05);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    }
    
    /* ---- Status Indicator ---- */
    .status-premium {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 16px;
        border-radius: 50px;
        background: rgba(0, 200, 100, 0.1);
        border: 1px solid rgba(0, 200, 100, 0.2);
        color: #00C864;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00C864;
        animation: pulse 2s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.5; transform: scale(1.2); }
    }
    
    /* ---- Footer Premium ---- */
    .footer-premium {
        text-align: center;
        padding: 40px 0 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        margin-top: 40px;
        position: relative;
    }
    
    .footer-premium::before {
        content: '';
        position: absolute;
        top: -1px;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--primary), var(--secondary), transparent);
    }
    
    /* ---- Progress Bar Personalizada ---- */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
        border-radius: 50px !important;
    }
    
    /* ---- Scrollbar Personalizada ---- */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 50px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, var(--primary), var(--secondary));
        border-radius: 50px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }
    
    /* ---- Mobile Responsive ---- */
    @media (max-width: 768px) {
        .glitch-text {
            font-size: 1.8rem;
        }
        
        .stat-number-premium {
            font-size: 1.8rem;
        }
        
        .founder-avatar-premium {
            width: 60px;
            height: 60px;
            font-size: 24px;
        }
    }
    
    /* ---- Animación de Entrada ---- */
    .fade-in {
        animation: fadeIn 0.6s ease-out;
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* ---- Tooltip Personalizado ---- */
    .tooltip-custom {
        position: relative;
        cursor: help;
    }
    
    .tooltip-custom:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 100%;
        left: 50%;
        transform: translateX(-50%);
        padding: 8px 16px;
        background: rgba(0, 0, 0, 0.9);
        color: white;
        border-radius: 8px;
        font-size: 0.8rem;
        white-space: nowrap;
        z-index: 100;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    </style>
    
    <!-- Grid de Fondo -->
    <div class="bg-grid"></div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# 4. SIDEBAR ULTRA PREMIUM
# ============================================================
with st.sidebar:
    # Logo y Marca
    st.markdown(
        """
        <div style="text-align: center; padding: 16px 0;">
            <div style="font-size: 3rem; margin-bottom: 8px;">⚡</div>
            <div style="font-family: 'Orbitron', sans-serif; 
                        font-size: 1.2rem; 
                        font-weight: 700; 
                        background: linear-gradient(135deg, #00D4FF, #7B2FBE);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;">
                TECNOLOGIA WARDE
            </div>
            <div style="color: #7B8DB0; font-size: 0.75rem; letter-spacing: 2px; margin-top: 4px;">
                INNOVACIÓN DIGITAL
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 16px 0;'>", unsafe_allow_html=True)
    
    # Navegación
    nav_items = [
        ("🏠", "Inicio"),
        ("💎", "Servicios"),
        ("👥", "Equipo"),
        ("💬", "Chat IA"),
        ("🌐", "Comunidad"),
        ("❓", "FAQ"),
        ("📱", "Contacto")
    ]
    
    for icon, label in nav_items:
        st.markdown(
            f"""
            <div style="
                padding: 10px 16px;
                margin: 4px 0;
                border-radius: 12px;
                color: #B0C4DE;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 12px;
                border: 1px solid transparent;
                hover: {
                    background: rgba(0, 212, 255, 0.05);
                    border-color: rgba(0, 212, 255, 0.1);
                }
            ">
                <span style="font-size: 1.2rem;">{icon}</span>
                <span style="font-weight: 500;">{label}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 16px 0;'>", unsafe_allow_html=True)
    
    # Estado del Sistema
    st.markdown(
        """
        <div class="status-premium">
            <span class="status-dot"></span>
            Sistema Activo 24/7
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown(
        """
        <div style="margin-top: 12px; color: #4A5070; font-size: 0.75rem;">
            <div>🕐 Horario: L-V 9am-8pm</div>
            <div>🤖 Soporte IA 24/7</div>
            <div>📍 República Dominicana</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 16px 0;'>", unsafe_allow_html=True)
    
    # Estadísticas de Sesión
    if "visit_count" not in st.session_state:
        st.session_state.visit_count = 0
    st.session_state.visit_count += 1
    
    st.markdown(
        f"""
        <div style="text-align: center; color: #4A5070; font-size: 0.75rem;">
            <div>👁️ Visitas: {st.session_state.visit_count}</div>
            <div style="margin-top: 4px;">⚡ Tiempo real</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ============================================================
# 5. BARRA DE CARGA CON EFECTO PREMIUM
# ============================================================
if "app_loaded" not in st.session_state:
    placeholder = st.empty()
    with placeholder.container():
        st.markdown(
            """
            <div style="text-align: center; padding: 40px 0;">
                <div style="font-family: 'Orbitron', sans-serif; 
                            color: #00D4FF; 
                            font-size: 1.2rem; 
                            margin-bottom: 16px;
                            letter-spacing: 2px;">
                    ⚡ Iniciando Tecnología Warde
                </div>
                <div style="font-size: 0.8rem; color: #7B8DB0;">
                    Cargando sistema de innovación digital...
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        barra = st.progress(0)
        for i in range(0, 101, 5):
            time.sleep(0.05)
            barra.progress(i)
    placeholder.empty()
    st.session_state.app_loaded = True
    AppState.add_notification("Bienvenido a Tecnología Warde 🚀", "success")
    st.toast("🚀 Tecnología Warde cargada exitosamente!", icon="⚡")

# ============================================================
# 6. CABECERA PRINCIPAL CON EFECTO GLITCH
# ============================================================
st.markdown(
    """
    <div style="text-align: center; padding: 20px 0 10px; position: relative; z-index: 1;">
        <div style="display: inline-block; 
                    padding: 4px 20px; 
                    background: rgba(0, 212, 255, 0.1);
                    border: 1px solid rgba(0, 212, 255, 0.2);
                    border-radius: 50px;
                    color: #00D4FF;
                    font-size: 0.7rem;
                    font-family: 'Orbitron', sans-serif;
                    letter-spacing: 3px;
                    margin-bottom: 16px;
                    backdrop-filter: blur(10px);">
            ✦ VERIFICADO · RD ✦
        </div>
        <div class="glitch-text">
            TECNOLOGIA WARDE
        </div>
        <p style="color: #7B8DB0; font-size: 1.1rem; margin-top: 12px; letter-spacing: 1px;">
            Transformando el futuro digital de la República Dominicana
        </p>
        <div style="display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; margin-top: 16px;">
            <span style="background: rgba(0, 212, 255, 0.05); padding: 4px 12px; border-radius: 50px; font-size: 0.7rem; color: #00D4FF; border: 1px solid rgba(0, 212, 255, 0.1);">
                🚀 Innovación
            </span>
            <span style="background: rgba(123, 47, 190, 0.05); padding: 4px 12px; border-radius: 50px; font-size: 0.7rem; color: #B57BEE; border: 1px solid rgba(123, 47, 190, 0.1);">
                💎 Calidad
            </span>
            <span style="background: rgba(255, 107, 107, 0.05); padding: 4px 12px; border-radius: 50px; font-size: 0.7rem; color: #FF6B6B; border: 1px solid rgba(255, 107, 107, 0.1);">
                ⚡ Rapidez
            </span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='border: none; height: 1px; background: linear-gradient(90deg, transparent, rgba(0,212,255,0.2), transparent); margin: 24px 0;'></div>", unsafe_allow_html=True)

# ============================================================
# 7. PRESENTACIÓN EMPRESARIAL CON ANIMACIÓN
# ============================================================
with st.container():
    col_intro1, col_intro2 = st.columns([2, 1])
    
    with col_intro1:
        st.markdown(
            """
            <div class="fade-in">
                <h2 style="color: #E0E6FF; font-family: 'Orbitron', sans-serif; font-size: 1.4rem;">
                    Bienvenido al Futuro Digital
                </h2>
                <p style="color: #B0C4DE; line-height: 1.8; font-size: 1.05rem;">
                    En <strong style="color: #00D4FF;">Tecnología Warde</strong>, fusionamos creatividad y 
                    tecnología para ofrecer soluciones digitales de vanguardia. Desde edición de video 
                    profesional hasta desarrollo web avanzado, cada proyecto es una obra maestra diseñada 
                    para superar expectativas.
                </p>
                <div style="display: flex; gap: 12px; flex-wrap: wrap; margin-top: 16px;">
                    <span style="padding: 6px 16px; background: rgba(0, 212, 255, 0.05); border-radius: 50px; border: 1px solid rgba(0, 212, 255, 0.1); color: #00D4FF; font-size: 0.85rem;">
                        ✅ 100% Digital
                    </span>
                    <span style="padding: 6px 16px; background: rgba(123, 47, 190, 0.05); border-radius: 50px; border: 1px solid rgba(123, 47, 190, 0.1); color: #B57BEE; font-size: 0.85rem;">
                        ✅ Garantía Total
                    </span>
                    <span style="padding: 6px 16px; background: rgba(255, 107, 107, 0.05); border-radius: 50px; border: 1px solid rgba(255, 107, 107, 0.1); color: #FF6B6B; font-size: 0.85rem;">
                        ✅ Soporte 24/7
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    with col_intro2:
        st.markdown(
            """
            <div class="neo-card" style="text-align: center; padding: 30px 20px;">
                <div style="font-size: 4rem; margin-bottom: 12px;">🌟</div>
                <div style="font-family: 'Orbitron', sans-serif; color: #00D4FF; font-size: 1.1rem;">
                    MISIÓN
                </div>
                <div style="color: #B0C4DE; font-size: 0.9rem; line-height: 1.6; margin-top: 8px;">
                    Democratizar la tecnología de calidad para todos en República Dominicana
                </div>
                <div style="margin-top: 12px; padding: 8px; background: rgba(0, 212, 255, 0.05); border-radius: 8px; border: 1px solid rgba(0, 212, 255, 0.05);">
                    <span style="color: #7B8DB0; font-size: 0.8rem;">Fundada en 2024</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='border: none; height: 1px; background: linear-gradient(90deg,

