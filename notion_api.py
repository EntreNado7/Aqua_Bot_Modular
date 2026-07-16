# ==========================================
# ARCHIVO: notion_api.py
# FUNCIÓN: Conexión segura con la base de datos de Notion.
# ==========================================

import os
import requests
from dotenv import load_dotenv

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
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    
    payload = {
        "filter": {
            "property": "Telefono",
            "rich_text": {
                "equals": telefono
            }
        }
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()
        
        if data.get("results"):
            # El cliente ya existe, regresamos el ID de su fila
            return data["results"][0]["id"]
        return None
    except Exception as e:
        print(f"Error al verificar cliente en Notion: {e}")
        return None

def registrar_lead(telefono, nombre="Prospecto", interes="General"):
    """
    Crea una nueva fila en Notion para un cliente que nos escribe por primera vez.
    """
    url = "https://api.notion.com/v1/pages"
    
    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Telefono": {
                "rich_text": [{"text": {"content": telefono}}]
            },
            "Nombre": {
                "title": [{"text": {"content": nombre}}]
            },
            "Interes": {
                "rich_text": [{"text": {"content": interes}}]
            },
            "Semaforo": {
                "select": {"name": "🟢"} # Inicia en verde por defecto
            }
        }
    }
    
    try:
        requests.post(url, headers=HEADERS, json=payload)
        print(f"Lead {telefono} registrado exitosamente.")
    except Exception as e:
        print(f"Error al registrar lead: {e}")

def solicitar_humano(page_id):
    """
    Actualiza la celda del Semáforo a color Amarillo 🟡 cuando piden un asesor.
    """
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    payload = {
        "properties": {
            "Semaforo": {
                "select": {"name": "🟡"}
            }
        }
    }
    
    try:
        requests.patch(url, headers=HEADERS, json=payload)
        print("Semáforo actualizado a Amarillo 🟡.")
    except Exception as e:
        print(f"Error al actualizar semáforo: {e}")