# ==========================================
# ARCHIVO: main.py
# FUNCIÓN: Motor principal omnicanal. Recibe, procesa y RESPONDE.
# ==========================================

import os
import re
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from thefuzz import process

# 📦 Importamos nuestros propios módulos
import respuestas
import notion_api
import menu_imagenes

app = Flask(__name__)

# Tokens de Meta (Guardados en Render)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
PAGE_TOKEN = os.getenv("PAGE_TOKEN") 


PAGE_TOKEN = os.getenv("PAGE_TOKEN") 
mensajes_procesados = set()  # <-- NUEVA LÍNEA: Libreta de mensajes atendidos
# ==========================================
# 🗣️ "CUERDAS VOCALES" (Envío a WhatsApp)
# ==========================================
def enviar_mensaje_wa(telefono, texto_respuesta, url_imagen=None, botones=None):
    """Envía texto, imagen o botones interactivos."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1️⃣ CASO: Enviar Botones Interactivos
    if botones:
        lista_botones = []
        for i, titulo in enumerate(botones):
            lista_botones.append({
                "type": "reply",
                "reply": {
                    "id": f"btn_{i}",
                    "title": titulo[:20] # Límite estricto de Meta
                }
            })
            
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": texto_respuesta},
                "action": {"buttons": lista_botones}
            }
        }
        
    # 2️⃣ CASO: Enviar Imagen con Texto
    elif url_imagen:
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "image",
            "image": {
                "link": url_imagen,
                "caption": texto_respuesta
            }
        }
        
    # 3️⃣ CASO: Enviar Texto Plano
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "text",
            "text": {"body": texto_respuesta}
        }
    
    try:
        respuesta = requests.post(url, headers=headers, json=payload)
        if respuesta.status_code == 200:
            print("Mensaje enviado con éxito a WA.")
        else:
            print(f"Error de Meta al enviar: {respuesta.text}")
    except Exception as e:
        print(f"Error interno al enviar: {e}")

# ==========================================
# 🗣️ "CUERDAS VOCALES" (Envío a FB/IG)
# ==========================================
def enviar_mensaje_messenger(sender_id, texto_respuesta):
    """Dispara la respuesta hacia Facebook Messenger o Instagram."""
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "recipient": {"id": sender_id},
        "message": {"text": texto_respuesta}
    }
    try:
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Error interno al enviar a Messenger: {e}")

# ==========================================
# ⏰ RELOJ INTERNO (Horario Hábil)
# ==========================================
def es_horario_habil():
    hora_actual = datetime.utcnow() - timedelta(hours=6)
    dia_semana = hora_actual.weekday() 
    hora = hora_actual.hour
    
    if 0 <= dia_semana <= 4:
        return 7 <= hora < 20
    elif dia_semana == 5:
        return 8 <= hora < 14
    return False

# ==========================================
# 🧠 LÓGICA PRINCIPAL DEL CHAT
# ==========================================
def procesar_mensaje(identificador, texto):
    texto = texto.lower().strip()
    
    # 1. VERIFICAR CLIENTE EN NOTION
    cliente_id = notion_api.verificar_cliente(identificador)
    if not cliente_id:
        notion_api.registrar_lead(identificador)
        texto_bienvenida = respuestas.MENSAJES["bienvenida_nueva"]
        # Primer envío de botones (Límite: 3, máx 20 caracteres)
        mis_botones = ["📍 Ubicación", "🕒 Horarios", "🏊‍♂️ Ver Clases"]
        return texto_bienvenida, None, mis_botones
    else:
        notion_api.actualizar_interaccion(cliente_id, texto)

    # 2. BOTÓN DE ASESOR (HANDOFF)
    if "asesor" in texto or "humano" in texto or "recepcion" in texto:
        notion_api.solicitar_humano(cliente_id)
        return respuestas.MENSAJES["traspaso_horario_habil"], None, None

    # 3. INTERACCIONES DE MENÚ PRINCIPAL (Botones Fijos)
    if texto in ["📍 ubicación", "ubicación", "ubicacion"]:
        return respuestas.MENSAJES["ubicacion"], None, None
    elif texto in ["🕒 horarios", "horarios"]:
        return respuestas.MENSAJES["horarios"], None, None
    elif texto in ["🏊‍♂️ ver clases", "ver clases"]:
        return respuestas.MENSAJES["menu_clases"], None, ["💦 Clases de Agua", "🌍 Clases de Tierra", "🎁 Paquetes Combo"]
    
    # 3.1 BIFURCACIONES DEL MENÚ DE AGUA
    elif texto in ["💦 clases de agua", "clases de agua", "agua"]:
        return respuestas.MENSAJES["menu_agua"], None, ["🧑 Adultos", "👧 Infantiles", "👶 Bebés"]
    elif texto in ["🧑 adultos", "adultos"]:
        return respuestas.MENSAJES["menu_adultos"], None, None
    elif texto in ["👧 infantiles", "infantiles"]:
        return respuestas.MENSAJES["menu_infantiles"], None, None
    elif texto in ["👶 bebés", "bebes"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["bebes"]
        return desc_texto, None, desc_botones
    elif texto in ["🌍 clases de tierra", "clases de tierra", "tierra"]:
        # Aquí puedes enganchar la info de tierra más adelante
        return "Nuestras clases de tierra incluyen Yoga, Spinning, GAP, Box... (Próximamente catálogo visual)", None, None

    # 4. FASE DE EXPLORACIÓN: Búsqueda de Descripciones (Texto Libre)
    opciones_descripciones = list(respuestas.DESCRIPCIONES.keys())
    coincidencia_desc, puntaje_desc = process.extractOne(texto, opciones_descripciones)
    if puntaje_desc >= 75:
        # Extraemos el texto y los botones dinámicos desde el diccionario
        texto_descripcion, botones_cierre = respuestas.DESCRIPCIONES[coincidencia_desc]
        return texto_descripcion, None, botones_cierre

    # 5. FASE DE CIERRE: Búsqueda de Imágenes (Por botón o texto de costos)
    mapeo_imagenes = {}
    for categoria, datos in menu_imagenes.CATALOGO_IMAGENES.items():
        for keyword in datos["palabras_clave"]:
            mapeo_imagenes[keyword] = categoria
            
    opciones_img = list(mapeo_imagenes.keys())
    coincidencia_img, puntaje_img = process.extractOne(texto, opciones_img)
    
    import random
    if puntaje_img >= 65:
        categoria_encontrada = mapeo_imagenes[coincidencia_img]
        datos_categoria = menu_imagenes.CATALOGO_IMAGENES[categoria_encontrada]
        texto_elegido = random.choice(datos_categoria["textos"])
        imagen_elegida = datos_categoria["links"][0] if datos_categoria["links"] else None
        
        return texto_elegido, imagen_elegida, None

    # 6. MENSAJE POR DEFECTO (Fallback)
    return respuestas.MENSAJES["no_entiendo"], None, None
# ==========================================
# 🌐 CONEXIÓN OMNICANAL (WEBHOOK)
# ==========================================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token de verificación inválido", 403
        
    elif request.method == "POST":
        datos = request.json
        try:
            for entry in datos.get("entry", []):
                
                # 🟢 CASO 1: WhatsApp
                if "changes" in entry:
                    cambios = entry["changes"][0]["value"]
                    if "messages" in cambios:
                        mensaje_data = cambios["messages"][0]
                        if "text" in mensaje_data or "interactive" in mensaje_data:
                            
                            # --- ESCUDO ANTI-DUPLICADOS ---
                            mensaje_id = mensaje_data.get("id")
                            if mensaje_id in mensajes_procesados:
                                continue 
                            mensajes_procesados.add(mensaje_id)
                            # ------------------------------
                            
                            # Extraemos el texto
                            if "interactive" in mensaje_data:
                                texto = mensaje_data["interactive"]["button_reply"]["title"]
                            else:
                                texto = mensaje_data["text"]["body"]
                                
                            telefono = cambios["contacts"][0]["wa_id"]
                            
                            if telefono.startswith("521") and len(telefono) == 13:
                                telefono = telefono.replace("521", "52", 1)
                            
                            # AQUÍ ESTÁ LA SOLUCIÓN: Desempaquetamos 3 valores
                            respuesta_texto, url_img, botones_interactivos = procesar_mensaje(telefono, texto)
                            enviar_mensaje_wa(telefono, respuesta_texto, url_img, botones_interactivos)
                            
                # 🔵🟣 CASO 2: Messenger / Instagram
                elif "messaging" in entry:
                    mensaje_data = entry["messaging"][0]
                    if "message" in mensaje_data and "text" in mensaje_data["message"]:
                        texto = mensaje_data["message"]["text"]
                        sender_id = mensaje_data["sender"]["id"]
                        
                        # AQUÍ TAMBIÉN: Desempaquetamos 3 valores
                        respuesta_texto, url_img, botones_interactivos = procesar_mensaje(sender_id, texto)
                        enviar_mensaje_messenger(sender_id, respuesta_texto)
                        
        except Exception as e:
            print(f"Error procesando mensaje: {e}") 
            
        return jsonify({"status": "ok"}), 200
