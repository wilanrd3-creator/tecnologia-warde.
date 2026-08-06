import streamlit as st
import streamlit.components.v1 as components
import urllib.parse
import sqlite3
import hmac
import random
import string
import csv
import io
from datetime import datetime, timezone, timedelta
import time
import json
import urllib.request
import os
import hashlib
import re
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64
import qrcode
from io import BytesIO
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from textblob import TextBlob
import pytz
import requests
import feedparser
import yfinance as yf
from bs4 import BeautifulSoup
import schedule
import threading
import calendar
import uuid
import jwt
import bcrypt
from captcha.image import ImageCaptcha
import pyotp
import qrcode
import phonenumbers
from phonenumbers import carrier, geocoder, timezone as phtimezone
import whois
import dns.resolver
import socket
import subprocess
import shutil
import zipfile
import tarfile
import tempfile
import markdown
import pdfkit
import docx
from docx.shared import Inches, Pt, RGBColor
from PIL import Image, ImageDraw, ImageFont
import pywhatkit as kit
import webbrowser
import psutil
import platform
import cpuinfo
import GPUtil
import netifaces
import speedtest
import ping3
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
import vega_datasets
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
from transformers import pipeline
import torch
import librosa
import soundfile as sf
import pyttsx3
import speech_recognition as sr
from googletrans import Translator
import langdetect
from deep_translator import GoogleTranslator
import qrcode
import barcode
from barcode.writer import ImageWriter
from PIL import Image
import pycountry
import country_converter as coco
import forex_python.converter
from forex_python.bitcoin import BtcConverter
import holidays
import lunar_python
import ephem
import skyfield
from astropy.time import Time
import geocoder
import geopy
from geopy.geocoders import Nominatim
import reverse_geocoder as rg
import folium
import branca
import matplotlib.patches as patches
from shapely.geometry import Point, Polygon
import osmium
import overpass
from scipy.spatial import Voronoi, voronoi_plot_2d
import networkx as nx
import igraph as ig
import community as community_louvain
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap
import openai
import anthropic
import cohere
import replicate
import elevenlabs
from elevenlabs import generate, play, Voice, VoiceSettings
import dlib
import face_recognition
import cv2
import mediapipe as mp
import tensorflow as tf
from tensorflow.keras import layers, models
import torchvision
from torchvision import transforms, models as torch_models
import gym
import pybullet
import pydub
from pydub import AudioSegment
import pyautogui
import keyboard
import mouse
import pynput
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener
import pyperclip
import webbrowser
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import praw
import tweepy
import facebook
import instagrapi
from instagrapi import Client
import youtube_dl
import yt_dlp
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import googleapiclient
from googleapiclient.discovery import build
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import dropbox
import google_drive
from google.oauth2 import service_account
import boto3
import azure.storage.blob
import redis
import memcache
import pymongo
from pymongo import MongoClient
import psycopg2
import mysql.connector
import firebase_admin
from firebase_admin import credentials, firestore, auth, storage
import twilio
from twilio.rest import Client as TwilioClient
import vonage
import africastalking
import telegram
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import discord
from discord import Intents, Client, Message, Embed
import slack_sdk
from slack_sdk import WebClient
from slack_sdk.webhook import WebhookClient
import mattermost
from mattermostdriver import Driver
import rocket_chat
from rocket_chat.api import RocketChatAPI
import matrix_client
from matrix_client.client import MatrixClient
import signal
import asyncio
import aiohttp
import websockets
import socketio
import pika
import kafka
from confluent_kafka import Producer, Consumer
import celery
from celery import Celery
import redis
import memcache
import elasticsearch
from elasticsearch import Elasticsearch
import influxdb
from influxdb import InfluxDBClient
import timescaledb
import questdb
import clickhouse
from clickhouse_driver import Client as ClickHouseClient
import snowflake.connector
import databricks
from databricks import sql
import trino
from trino.dbapi import connect as trino_connect
import presto
from pyhive import presto as pyhive_presto
import impala
from impala.dbapi import connect as impala_connect
import hdfs
from hdfs import InsecureClient
import webhdfs
import gcsfs
import s3fs
import azurefs
import minio
from minio import Minio
import neo4j
from neo4j import GraphDatabase
import arangodb
from arangodb import ArangoClient
import cassandra
from cassandra.cluster import Cluster
import scylla
from scylla.driver import Cluster as ScyllaCluster
import cockroachdb
from cockroachdb import sql as cockroach_sql
import tidb
from tidb import connect as tidb_connect
import milvus
from milvus import MilvusClient
import weaviate
import pinecone
import chromadb
import qdrant_client
import redis_om
import mongoengine
import beanie
from beanie import Document, init_beanie
import motor.motor_asyncio
import asyncpg
import asyncpg.pool
import aiosqlite
import aiopg
import aiomysql
import aioredis
import aiobotocore
import httpx
import aiohttp
import asyncio
import nest_asyncio
nest_asyncio.apply()

# ============================================================
# 1. CONFIGURACIÓN CENTRAL - MEGA MAX
# ============================================================

# Todos los servicios con más detalles
SERVICIOS = {
    "Edicion de Video Corto (TikTok/Reels/Shorts)": {
        "min": 100, "max": 150, "unidad": "por video",
        "descripcion": "Edición profesional con subtítulos, efectos y música",
        "tiempo": "24-48 horas",
        "incluye": ["Subtítulos dinámicos", "Efectos visuales", "Música sincronizada", "2 revisiones"],
        "categoria": "Multimedia",
        "tags": ["video", "reels", "tiktok", "shorts", "edicion"]
    },
    "Miniatura de YouTube": {
        "min": 150, "max": 150, "unidad": "por diseño",
        "descripcion": "Diseños con alto CTR para maximizar clics",
        "tiempo": "24 horas",
        "incluye": ["3 variantes", "Texto optimizado", "Colores llamativos"],
        "categoria": "Multimedia",
        "tags": ["youtube", "thumbnail", "miniatura", "diseno"]
    },
    "Pagina Web (Streamlit/Anvil)": {
        "min": 700, "max": 1000, "unidad": "por proyecto",
        "descripcion": "Sitios web modernos e interactivos",
        "tiempo": "5-7 días",
        "incluye": ["Diseño responsive", "Formularios", "Base de datos", "Despliegue"],
        "categoria": "Programación",
        "tags": ["web", "streamlit", "anvil", "python", "desarrollo"]
    },
    "Servidor de Discord": {
        "min": 300, "max": 400, "unidad": "por proyecto",
        "descripcion": "Configuración completa con bots y roles",
        "tiempo": "2-3 días",
        "incluye": ["Canales organizados", "Roles personalizados", "Bots automáticos"],
        "categoria": "Programación",
        "tags": ["discord", "bot", "servidor", "comunidad"]
    },
    "Paquete de Posts para Redes Sociales": {
        "min": 150, "max": 300, "unidad": "por diseño",
        "descripcion": "Contenido visual para redes sociales",
        "tiempo": "24-48 horas",
        "incluye": ["Diseños en múltiples formatos", "Textos optimizados", "Calendarización"],
        "categoria": "Diseño",
        "tags": ["redes sociales", "instagram", "facebook", "posts"]
    },
    "Invitacion Digital": {
        "min": 200, "max": 200, "unidad": "por diseño",
        "descripcion": "Invitaciones personalizadas para eventos",
        "tiempo": "24 horas",
        "incluye": ["Diseño único", "Texto personalizado", "Formato digital"],
        "categoria": "Diseño",
        "tags": ["invitacion", "evento", "digital", "tarjeta"]
    },
}

# Más niveles de urgencia
RECARGO_URGENCIA = {
    "Normal (5-7 dias)": 1.0,
    "Rapido (2-3 dias)": 1.15,
    "Urgente (24-48 horas)": 1.35,
    "Express (12-24 horas)": 1.50,
    "Super Express (4-8 horas)": 1.80,
    "Relampago (1-4 horas)": 2.0,
    "Instantaneo (30 min - 1 hora)": 2.5,
}

# Cupones más variados
CUPONES = {
    "WARDE10": 0.10,
    "BIENVENIDO15": 0.15,
    "CLIENTEVIP": 0.20,
    "SUPERWARDE": 0.25,
    "PRIMERAORDEN": 0.30,
    "REFERIDO": 0.15,
    "BLACKFRIDAY": 0.40,
    "CYBERMONDAY": 0.35,
    "NAVIDAD": 0.25,
    "ANIVERSARIO": 0.30,
    "AMIGO": 0.15,
    "100SEGUIDORES": 0.10,
}

# Niveles de gamificación expandidos
NIVELES = {
    "Bronce": {"puntos": 0, "color": "#CD7F32", "descuento": 0.05, "beneficios": ["Descuento 5%", "Acceso a promociones"]},
    "Plata": {"puntos": 100, "color": "#C0C0C0", "descuento": 0.10, "beneficios": ["Descuento 10%", "Prioridad en atención", "1 revisión extra"]},
    "Oro": {"puntos": 300, "color": "#FFD700", "descuento": 0.15, "beneficios": ["Descuento 15%", "Soporte VIP", "3 revisiones extras"]},
    "Platino": {"puntos": 500, "color": "#E5E4E2", "descuento": 0.20, "beneficios": ["Descuento 20%", "Atención 24/7", "Revisiones ilimitadas"]},
    "Diamante": {"puntos": 1000, "color": "#B9F2FF", "descuento": 0.30, "beneficios": ["Descuento 30%", "Gerente dedicado", "Prioridad total", "Descuentos especiales"]},
    "Rubi": {"puntos": 2000, "color": "#E0115F", "descuento": 0.40, "beneficios": ["Descuento 40%", "Asesor personal", "Eventos exclusivos"]},
    "Esmeralda": {"puntos": 5000, "color": "#50C878", "descuento": 0.50, "beneficios": ["Descuento 50%", "Socios estratégicos", "Inversión directa"]},
}

DB_PATH = "warde_datos.db"

# ============================================================
# 2. BASE DE DATOS - 50 TABLAS
# ============================================================

@st.cache_resource
def obtener_conexion_bd():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    
    # Tablas principales (10)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mensajes_globales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TEXT NOT NULL,
            verificado INTEGER NOT NULL DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ordenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL UNIQUE,
            nombre TEXT NOT NULL,
            contacto TEXT NOT NULL,
            email TEXT,
            servicio TEXT NOT NULL,
            presupuesto TEXT,
            urgencia TEXT,
            detalles TEXT,
            estado TEXT NOT NULL DEFAULT 'Recibido',
            fecha TEXT NOT NULL,
            puntos_ganados INTEGER DEFAULT 0,
            feedback TEXT,
            fecha_entrega TEXT,
            valoracion INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS resenas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            comentario TEXT NOT NULL,
            estrellas INTEGER NOT NULL,
            aprobado INTEGER NOT NULL DEFAULT 0,
            fecha TEXT NOT NULL,
            video_url TEXT,
            servicio_id TEXT,
            like INTEGER DEFAULT 0,
            dislike INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT NOT NULL,
            email TEXT,
            interes TEXT,
            fecha TEXT NOT NULL,
            puntos INTEGER DEFAULT 0,
            nivel TEXT DEFAULT 'Bronce',
            fuente TEXT DEFAULT 'Web',
            ultima_interaccion TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT NOT NULL,
            email TEXT,
            fecha_cita TEXT NOT NULL,
            hora_cita TEXT NOT NULL,
            motivo TEXT,
            estado TEXT NOT NULL DEFAULT 'Pendiente',
            fecha_creacion TEXT NOT NULL,
            recordatorio_enviado INTEGER DEFAULT 0,
            confirmado INTEGER DEFAULT 0,
            duracion INTEGER DEFAULT 30
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS baneados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor TEXT NOT NULL UNIQUE,
            motivo TEXT,
            fecha TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS visitas_globales (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            total INTEGER NOT NULL DEFAULT 0,
            hoy INTEGER DEFAULT 0,
            mes INTEGER DEFAULT 0,
            unique_visitantes INTEGER DEFAULT 0,
            ultima_visita TEXT
        )
    """)
    conn.execute("INSERT OR IGNORE INTO visitas_globales (id, total, hoy, mes, unique_visitantes) VALUES (1, 0, 0, 0, 0)")
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS anuncio_fijado (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            texto TEXT,
            fecha TEXT,
            tipo TEXT DEFAULT 'info',
            activo INTEGER DEFAULT 1,
            prioridad INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS log_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            detalle TEXT NOT NULL,
            fecha TEXT NOT NULL,
            ip TEXT,
            usuario TEXT,
            categoria TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mensajes_privados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            remitente TEXT NOT NULL,
            destinatario TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TEXT NOT NULL,
            leido INTEGER DEFAULT 0,
            orden_id TEXT,
            adjunto TEXT
        )
    """)
    
    # Tablas de gamificación (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS puntos_usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            puntos INTEGER DEFAULT 0,
            nivel TEXT DEFAULT 'Bronce',
            ultima_actividad TEXT,
            total_compras INTEGER DEFAULT 0,
            total_gastado REAL DEFAULT 0,
            referrals INTEGER DEFAULT 0,
            logros TEXT DEFAULT '[]'
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            puntos_requeridos INTEGER DEFAULT 0,
            icono TEXT DEFAULT '🏆'
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS misiones_diarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            puntos_recompensa INTEGER DEFAULT 10,
            fecha TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS historial_puntos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            puntos INTEGER NOT NULL,
            accion TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rankings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            categoria TEXT NOT NULL,
            posicion INTEGER DEFAULT 0,
            fecha TEXT NOT NULL
        )
    """)
    
    # Tablas de contenido (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS encuestas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta TEXT NOT NULL,
            respuestas TEXT,
            fecha TEXT NOT NULL,
            activa INTEGER DEFAULT 1,
            votos_totales INTEGER DEFAULT 0,
            categoria TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pregunta TEXT NOT NULL,
            respuesta TEXT NOT NULL,
            categoria TEXT,
            orden INTEGER DEFAULT 0,
            activo INTEGER DEFAULT 1,
            votos_utiles INTEGER DEFAULT 0,
            vistas INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wishlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            servicio TEXT NOT NULL,
            fecha TEXT NOT NULL,
            notificar INTEGER DEFAULT 1,
            prioridad INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS testimonios_video (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            video_url TEXT NOT NULL,
            descripcion TEXT,
            fecha TEXT NOT NULL,
            aprobado INTEGER DEFAULT 0,
            duracion INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS portafolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            categoria TEXT,
            imagen_url TEXT,
            video_url TEXT,
            fecha TEXT NOT NULL,
            destacado INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0
        )
    """)
    
    # Tablas de marketing (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS suscriptores_email (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            nombre TEXT,
            fecha TEXT NOT NULL,
            activo INTEGER DEFAULT 1,
            confirmed INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS campañas_email (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            contenido TEXT,
            fecha_envio TEXT,
            destinatarios INTEGER DEFAULT 0,
            abiertos INTEGER DEFAULT 0,
            clics INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notificaciones_push (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL,
            titulo TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TEXT NOT NULL,
            leido INTEGER DEFAULT 0,
            tipo TEXT DEFAULT 'info'
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS plantillas_email (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            asunto TEXT,
            cuerpo TEXT,
            categoria TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS segmentos_clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            condiciones TEXT,
            tamano INTEGER DEFAULT 0
        )
    """)
    
    # Tablas de analytics (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics_diarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            visitas INTEGER DEFAULT 0,
            conversiones INTEGER DEFAULT 0,
            ingresos REAL DEFAULT 0,
            servicios_vendidos INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS metricas_realtime (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metrica TEXT NOT NULL,
            valor TEXT,
            timestamp TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predicciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor TEXT,
            fecha_prediccion TEXT NOT NULL,
            precision REAL DEFAULT 0.0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS heatmaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pagina TEXT NOT NULL,
            clicks TEXT,
            scroll TEXT,
            fecha TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS funnel_conversion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            paso TEXT NOT NULL,
            usuarios INTEGER DEFAULT 0,
            conversion REAL DEFAULT 0.0,
            fecha TEXT NOT NULL
        )
    """)
    
    # Tablas de integraciones (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS webhooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            url TEXT NOT NULL,
            eventos TEXT,
            activo INTEGER DEFAULT 1,
            fecha_creacion TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS apis_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servicio TEXT NOT NULL,
            api_key TEXT,
            config TEXT,
            activo INTEGER DEFAULT 1
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS integraciones_activas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL,
            activo INTEGER DEFAULT 1,
            config TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs_sistema (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nivel TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            modulo TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS health_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            servicio TEXT NOT NULL,
            estado TEXT,
            ultimo_check TEXT,
            tiempo_respuesta REAL DEFAULT 0.0
        )
    """)
    
    # Tablas de inventario (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            precio REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            categoria TEXT,
            proveedor TEXT,
            sku TEXT UNIQUE,
            fecha_creacion TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS inventario_movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            usuario TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS proveedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            contacto TEXT,
            email TEXT,
            telefono TEXT,
            direccion TEXT,
            rating INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categorias_productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            padre_id INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS precios_historicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            precio REAL NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    
    # Tablas de recursos humanos (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE,
            telefono TEXT,
            puesto TEXT,
            departamento TEXT,
            fecha_contratacion TEXT,
            salario REAL DEFAULT 0.0,
            activo INTEGER DEFAULT 1
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS horarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            dia_semana INTEGER NOT NULL,
            hora_inicio TEXT,
            hora_fin TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vacaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            fecha_inicio TEXT NOT NULL,
            fecha_fin TEXT NOT NULL,
            aprobado INTEGER DEFAULT 0,
            motivo TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS rendimiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            mes TEXT NOT NULL,
            productividad REAL DEFAULT 0.0,
            calidad REAL DEFAULT 0.0,
            puntualidad REAL DEFAULT 0.0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS capacitaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empleado_id INTEGER NOT NULL,
            curso TEXT NOT NULL,
            fecha TEXT NOT NULL,
            duracion INTEGER DEFAULT 0,
            certificado INTEGER DEFAULT 0
        )
    """)
    
    # Tablas de proyectos (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cliente TEXT,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            estado TEXT DEFAULT 'Planificacion',
            presupuesto REAL DEFAULT 0.0,
            prioridad INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            asignado_a TEXT,
            estado TEXT DEFAULT 'Pendiente',
            fecha_limite TEXT,
            prioridad INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sprints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            fecha_inicio TEXT,
            fecha_fin TEXT,
            objetivo TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comentarios_tarea (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea_id INTEGER NOT NULL,
            usuario TEXT NOT NULL,
            comentario TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS adjuntos_proyecto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proyecto_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            url TEXT,
            fecha_subida TEXT
        )
    """)
    
    # Tablas de finanzas (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            servicio TEXT NOT NULL,
            monto REAL NOT NULL,
            estado TEXT DEFAULT 'Pendiente',
            fecha TEXT NOT NULL,
            metodo_pago TEXT,
            referencia TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS facturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE NOT NULL,
            cliente TEXT NOT NULL,
            monto REAL NOT NULL,
            impuesto REAL DEFAULT 0.0,
            fecha_emision TEXT,
            fecha_vencimiento TEXT,
            estado TEXT DEFAULT 'Pendiente',
            pdf_url TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS gastos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT NOT NULL,
            monto REAL NOT NULL,
            categoria TEXT,
            fecha TEXT NOT NULL,
            comprobante TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS presupuestos_mensuales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            ingreso_esperado REAL DEFAULT 0.0,
            gasto_esperado REAL DEFAULT 0.0,
            ingreso_real REAL DEFAULT 0.0,
            gasto_real REAL DEFAULT 0.0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cuentas_bancarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            banco TEXT NOT NULL,
            tipo TEXT NOT NULL,
            numero TEXT UNIQUE,
            saldo REAL DEFAULT 0.0,
            moneda TEXT DEFAULT 'DOP'
        )
    """)
    
    # Tablas de soporte (5)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            asunto TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'Abierto',
            prioridad TEXT DEFAULT 'Normal',
            fecha_creacion TEXT,
            fecha_cierre TEXT,
            asignado_a TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS respuestas_ticket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            usuario TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS categorias_ticket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS soluciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            solucion TEXT,
            tiempo_resolucion INTEGER DEFAULT 0
        )
    """)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS encuestas_satisfaccion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            puntuacion INTEGER DEFAULT 0,
            comentario TEXT,
            fecha TEXT
        )
    """)
    
    # Tablas adicionales (20)
    conn.execute("""CREATE TABLE IF NOT EXISTS backups (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, tamano REAL, ubicacion TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS auditoria (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, accion TEXT, tabla TEXT, fecha TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS configuracion (id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT UNIQUE, valor TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS migraciones (id INTEGER PRIMARY KEY AUTOINCREMENT, version TEXT, fecha TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS cache (id INTEGER PRIMARY KEY AUTOINCREMENT, clave TEXT UNIQUE, valor TEXT, expiracion INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS sesiones (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, token TEXT, fecha_creacion TEXT, expiracion INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS permisos (id INTEGER PRIMARY KEY AUTOINCREMENT, rol TEXT, permiso TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS roles (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, descripcion TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS actividad (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, accion TEXT, detalles TEXT, fecha TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS sincronizacion (id INTEGER PRIMARY KEY AUTOINCREMENT, tabla TEXT, ultima_sincronizacion TEXT, estado TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS reportes (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT, query TEXT, formato TEXT, programado INTEGER)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS favoritos (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, item TEXT, categoria TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS etiquetas (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE, color TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS relaciones (id INTEGER PRIMARY KEY AUTOINCREMENT, entidad1 TEXT, entidad2 TEXT, tipo TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS historial_cambios (id INTEGER PRIMARY KEY AUTOINCREMENT, entidad TEXT, id_entidad INTEGER, cambio TEXT, fecha TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS notificaciones_usuario (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, mensaje TEXT, leido INTEGER, fecha TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS preferencias_usuario (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT UNIQUE, preferencias TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS interacciones (id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, accion TEXT, elemento TEXT, fecha TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS meta_datos (id INTEGER PRIMARY KEY AUTOINCREMENT, entidad TEXT, clave TEXT, valor TEXT)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS validaciones (id INTEGER PRIMARY KEY AUTOINCREMENT, regla TEXT, campo TEXT, mensaje TEXT)""")
    
    conn.commit()
    return conn

# ============================================================
# 3.