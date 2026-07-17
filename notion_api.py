# ==========================================
# ARCHIVO: notion_api.py
# FUNCIÓN: Conexión segura con la base de datos de Notion.
# ==========================================

import os
import requests
from dotenv import load_dotenv
from datetime import datetime  # <-- Agrega esta línea nueva

# Cargamos las llaves secretas de forma segura
load_dotenv()
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def verificar_cliente(telefono):
    """
    Busca si el número de teléfono ya existe en la base de datos de Notion.
    Retorna el ID de la página si existe, o None si es un cliente nuevo.
    """
    # URL corregida: https://api.notion.com/...
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    payload = {
        "filter": {
            "property": "Telefono",
            "title": {  
                "equals": telefono
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()
        
        if data.get("results"):
            return data["results"][0]["id"]
        return None
    except Exception as e:
        print(f"Error al verificar cliente en Notion: {e}")
        return None

def registrar_lead(telefono, canal="WhatsApp", interes="General"):
    """
    Crea una nueva fila en Notion llenando todas las columnas.
    """
    url = "https://api.notion.com/v1/pages"
    
    # Obtenemos la fecha actual para la columna Fecha
    fecha_actual = datetime.utcnow().isoformat()
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Telefono": {
                "title": [{"text": {"content": telefono}}]
            },
            "Fecha": {
                "date": {"start": fecha_actual}
            },
            "ulitmo_mensaje": {  # Escrito exactamente como en tu tabla
                "rich_text": [{"text": {"content": "Primer contacto"}}]
            },
            "Perfil_WA_FB_IG": {
                "rich_text": [{"text": {"content": "Usuario Nuevo"}}]
            },
            "Canal": {
                "rich_text": [{"text": {"content": canal}}]
            },
            "Interes": {
                "rich_text": [{"text": {"content": interes}}]
            },
            "Estado_Atencion": { 
                "rich_text": [{"text": {"content": "🟢 Automático"}}] 
            },
            "Solicitud_Pendiente": {
                "rich_text": [{"text": {"content": "Ninguna"}}]
            }
        }
    }
    
    try:
        requests.post(url, headers=HEADERS, json=payload)
        print(f"Lead {telefono} registrado con todas las columnas.")
    except Exception as e:
        print(f"Error al registrar lead: {e}")

def solicitar_humano(page_id):
    """
    Actualiza la celda del Estado a color Amarillo 🟡 cuando piden un asesor.
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    payload = {
        "properties": {
            "Estado_Atencion": { # Corregido al nombre exacto de tu columna
                "rich_text": [{"text": {"content": "🟡 Requiere Asesor"}}]
            }
        }
    }
    
    try:
        requests.patch(url, headers=HEADERS, json=payload)
        print("Estado actualizado a Amarillo 🟡.")
    except Exception as e:
        print(f"Error al actualizar estado: {e}")
