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

def verificar_cliente(identificador):
    """Verifica si el cliente existe y devuelve su ID junto con la fecha de su última interacción."""
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    payload = {
        "filter": {
            "property": "Telefono", # Ajusta este nombre si tu columna se llama diferente (ej. "title")
            "title": {
                "equals": identificador
            }
        }
    }
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()
        results = data.get("results", [])
        if results:
            page_id = results[0]["id"]
            
            # Extraemos la fecha del último mensaje registrado
            props = results[0].get("properties", {})
            fecha_iso = None
            if "Fecha" in props and "date" in props["Fecha"] and props["Fecha"]["date"]:
                fecha_iso = props["Fecha"]["date"]["start"]
                
            return page_id, fecha_iso # Ahora devolvemos 2 datos
            
        return None, None
    except Exception as e:
        print(f"Error al verificar cliente: {e}")
        return None, None


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



def obtener_historial(page_id):
    """Obtiene el historial de interacciones del cliente desde Notion."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        prop_historial = data.get("properties", {}).get("Historial", {}).get("rich_text", [])
        if prop_historial:
            return prop_historial[0].get("plain_text", "")
        return ""
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return ""

def obtener_historial(page_id):
    """Obtiene el historial de interacciones del cliente desde Notion."""
    url = f"https://api.notion.com/v1/pages/{page_id}"
    try:
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        prop_historial = data.get("properties", {}).get("Historial", {}).get("rich_text", [])
        if prop_historial:
            return prop_historial[0].get("plain_text", "")
        return ""
    except Exception as e:
        print(f"Error al obtener historial: {e}")
        return ""

def actualizar_interaccion(page_id, texto):
    """Actualiza el último mensaje y concatena el nuevo clic al Historial."""
    # 1. Recuperamos la memoria anterior
    historial_previo = obtener_historial(page_id)
    
    # 2. Armamos la cadena de clics
    if historial_previo:
        nuevo_historial = f"{historial_previo} > {texto}"
        # Recortamos a los últimos 500 caracteres para no saturar la base de datos
        nuevo_historial = nuevo_historial[-500:]
    else:
        nuevo_historial = texto

    url = f"https://api.notion.com/v1/pages/{page_id}"
    payload = {
        "properties": {
            "ulitmo_mensaje": { # Escrito exactamente como en tu captura de Notion
                "rich_text": [{"text": {"content": texto}}]
            },
            "Historial": { # Tu nueva columna
                "rich_text": [{"text": {"content": nuevo_historial}}]
            }
        }
    }
    try:
        requests.patch(url, headers=HEADERS, json=payload)
    except Exception as e:
        print(f"Error al actualizar interaccion: {e}")
