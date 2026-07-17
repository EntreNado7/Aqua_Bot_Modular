# ==========================================
# ARCHIVO: main.py
# FUNCIÓN: Motor principal omnicanal (WhatsApp, FB Messenger, Instagram).
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

# Tokens de Meta (Se guardarán en Render)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
PAGE_TOKEN = os.getenv("PAGE_TOKEN") # Token futuro para responder en FB/IG

# ==========================================
# ⏰ RELOJ INTERNO (Horario Hábil)
# ==========================================
def es_horario_habil():
    """Calcula si la hora actual de México (UTC-6) está dentro del horario de atención."""
    hora_actual = datetime.utcnow() - timedelta(hours=6)
    dia_semana = hora_actual.weekday() # 0 = Lunes, 5 = Sábado, 6 = Domingo
    hora = hora_actual.hour
    
    if 0 <= dia_semana <= 4: # Lunes a Viernes (7:00 AM - 8:00 PM)
        return 7 <= hora < 20
    elif dia_semana == 5: # Sábados (8:00 AM - 2:00 PM)
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
        return "Bienvenida enviada"

    # 2. BOTÓN DE ASESOR (HANDOFF)
    if "asesor" in texto or "humano" in texto:
        notion_api.solicitar_humano(cliente_id)
        return "Traspaso procesado"

    # 3. FILTRO DE EDAD (REGLA MENORES DE 6 AÑOS)
    if re.search(r'\b([1-5])\s*(año|ano|añito)', texto):
        return "Filtro de edad aplicado"

    # 4. BUSCADOR INTELIGENTE EN EL CATÁLOGO (FUZZY MATCHING)
    todas_palabras = []
    for key, data in menu_imagenes.CATALOGO_IMAGENES.items():
        todas_palabras.extend(data["palabras_clave"])
    
    mejor_coincidencia = process.extractOne(texto, todas_palabras)
    
    if mejor_coincidencia and mejor_coincidencia[1] >= 85:
        palabra_encontrada = mejor_coincidencia[0]
        return f"Catálogo enviado por coincidencia con: {palabra_encontrada}"
        
    # 5. MENSAJE POR DEFECTO (NO ENTENDIÓ)
    return "Mensaje no entendido"

# ==========================================
# 🌐 CONEXIÓN OMNICANAL (WEBHOOK)
# ==========================================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Meta verifica que somos nosotros (Funciona igual para las 3 redes)
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token de verificación inválido", 403
        
    elif request.method == "POST":
        datos = request.json
        try:
            for entry in datos.get("entry", []):
                
                # 🟢 CASO 1: Es un paquete de WhatsApp
                if "changes" in entry:
                    cambios = entry["changes"][0]["value"]
                    if "messages" in cambios:
                        mensaje_data = cambios["messages"][0]
                        if "text" in mensaje_data:
                            texto = mensaje_data["text"]["body"]
                            telefono = cambios["contacts"][0]["wa_id"]
                            procesar_mensaje(telefono, texto)
                            
                # 🔵🟣 CASO 2: Es un paquete de Facebook Messenger o Instagram
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
