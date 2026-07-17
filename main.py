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

# ==========================================
# 🗣️ "CUERDAS VOCALES" (Envío a WhatsApp)
# ==========================================
def enviar_mensaje_wa(telefono, texto_respuesta):
    """Toma la respuesta del bot y la dispara hacia el celular del cliente."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
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
        return "¡Hola! Soy Aqua 💧, el asistente virtual de Acuática. Parece que eres nuevo por aquí. ¿En qué te puedo ayudar hoy? (Ej. Horarios, Costos, Ubicación)"

    # 2. BOTÓN DE ASESOR (HANDOFF)
    if "asesor" in texto or "humano" in texto:
        notion_api.solicitar_humano(cliente_id)
        return "¡Claro! He notificado a uno de nuestros asesores. Te contactarán lo más pronto posible."

    # 3. INTELIGENCIA CONVERSACIONAL (TheFuzz)
    # Lista de "intenciones" que Aqua sabe reconocer
    intenciones = ["horarios", "costos", "ubicacion", "promociones", "requisitos"]
    
    # TheFuzz compara el texto del usuario con nuestras intenciones y le da una calificación (0 a 100)
    coincidencia, puntaje = process.extractOne(texto, intenciones)
    
    # Si la similitud es del 70% o más (Entiende "orarios", "prezios", "uvicacion", etc.)
    if puntaje >= 70:
        # Extraemos la respuesta exacta desde tu archivo respuestas.py
        try:
            return respuestas.MENSAJES[coincidencia]
        except AttributeError:
            return f"Entendí que buscas información sobre '{coincidencia}', pero me falta conectar esa respuesta en mi sistema."

    # 4. MENSAJE POR DEFECTO
    return "No estoy muy segura de entender. 😅 ¿Podrías intentar con palabras clave como 'Horarios', 'Costos' o pedir hablar con un 'Asesor'?"

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
                            
                            # Procesamos y ENVIAMOS respuesta
                            respuesta = procesar_mensaje(telefono, texto)
                            enviar_mensaje_wa(telefono, respuesta)
                            
                # 🔵🟣 CASO 2: Messenger / Instagram
                elif "messaging" in entry:
                    mensaje_data = entry["messaging"][0]
                    if "message" in mensaje_data and "text" in mensaje_data["message"]:
                        texto = mensaje_data["message"]["text"]
                        sender_id = mensaje_data["sender"]["id"]
                        
                        procesar_mensaje(sender_id, texto)
                        
        except Exception as e:
            print(f"Error procesando mensaje: {e}") 
            
        return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
