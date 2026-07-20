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
def enviar_mensaje_wa(telefono, texto_respuesta, url_imagen=None):
    """Envía un mensaje de texto, o una imagen con texto adjunto (caption)."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # Si la función recibe una URL de imagen, arma un paquete multimedia
    if url_imagen:
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "image",
            "image": {
                "link": url_imagen,
                "caption": texto_respuesta
            }
        }
    # Si no hay imagen, manda texto normal
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
        return respuestas.MENSAJES["bienvenida_nueva"], None

    # 2. BOTÓN DE ASESOR (HANDOFF)
    if "asesor" in texto or "humano" in texto or "recepcion" in texto:
        notion_api.solicitar_humano(cliente_id)
        return respuestas.MENSAJES["traspaso_horario_habil"], None

    # 3. INTELIGENCIA CONVERSACIONAL (TheFuzz + Catálogo Visual)
    # Creamos un mapa relacionando cada palabra clave con su categoría
    mapeo_palabras = {}
    for categoria, datos in menu_imagenes.CATALOGO_IMAGENES.items():
        for keyword in datos["palabras_clave"]:
            mapeo_palabras[keyword] = categoria
            
    # TheFuzz compara el mensaje del cliente contra TODAS las palabras clave
    opciones = list(mapeo_palabras.keys())
    coincidencia, puntaje = process.extractOne(texto, opciones)
    
    # Si la coincidencia es buena (65% o más de similitud)
    import random
    print(f"Palabra detectada: {coincidencia} | Puntuación: {puntaje}")
    if puntaje >= 65:
        categoria_encontrada = mapeo_palabras[coincidencia]
        datos_categoria = menu_imagenes.CATALOGO_IMAGENES[categoria_encontrada]
        
        texto_elegido = random.choice(datos_categoria["textos"])
        # Tomamos el primer enlace de la lista de links
        imagen_elegida = datos_categoria["links"][0] if datos_categoria["links"] else None
        
        return texto_elegido, imagen_elegida

    # 4. MENSAJE POR DEFECTO (Fallback)
    return respuestas.MENSAJES["no_entiendo"], None
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
                        if "text" in mensaje_data:
                            texto = mensaje_data["text"]["body"]
                            telefono = cambios["contacts"][0]["wa_id"]
                            
                            # 🇲🇽 PARCHE PARA MÉXICO: Quitar el '1' de los números 521...
                            if telefono.startswith("521") and len(telefono) == 13:
                                telefono = telefono.replace("521", "52", 1)
                            
                            # Procesamos y ENVIAMOS respuesta (Atrapando texto e imagen)
                            respuesta_texto, url_img = procesar_mensaje(telefono, texto)
                            enviar_mensaje_wa(telefono, respuesta_texto, url_img)
                            
                # 🔵🟣 CASO 2: Messenger / Instagram
                elif "messaging" in entry:
                    mensaje_data = entry["messaging"][0]
                    if "message" in mensaje_data and "text" in mensaje_data["message"]:
                        texto = mensaje_data["message"]["text"]
                        sender_id = mensaje_data["sender"]["id"]
                        
                        # Atrapamos respuesta, pero en Messenger enviamos texto por ahora
                        # (La función de IG/FB aún necesita ajuste para imágenes)
                        respuesta_texto, url_img = procesar_mensaje(sender_id, texto)
                        enviar_mensaje_messenger(sender_id, respuesta_texto)
                        
        except Exception as e:
            print(f"Error procesando mensaje: {e}") 
            
        return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
