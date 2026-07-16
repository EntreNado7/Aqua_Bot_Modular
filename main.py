# ==========================================
# ARCHIVO: main.py
# FUNCIÓN: Motor principal del bot. Recibe, procesa y responde.
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

# Tokens de WhatsApp (Se guardarán en Render más adelante)
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")

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
def procesar_mensaje(telefono, texto):
    texto = texto.lower().strip()
    
    # 1. VERIFICAR CLIENTE EN NOTION
    cliente_id = notion_api.verificar_cliente(telefono)
    if not cliente_id:
        notion_api.registrar_lead(telefono)
        # Aquí enviaríamos el mensaje de respuestas.MENSAJES["bienvenida_nueva"]
        return "Bienvenida enviada"

    # 2. BOTÓN DE ASESOR (HANDOFF)
    if "asesor" in texto or "humano" in texto:
        notion_api.solicitar_humano(cliente_id)
        if es_horario_habil():
            mensaje_respuesta = respuestas.MENSAJES["traspaso_horario_habil"]
        else:
            mensaje_respuesta = respuestas.MENSAJES["traspaso_fuera_horario"]
        # Aquí enviaríamos mensaje_respuesta a WhatsApp
        return "Traspaso procesado"

    # 3. FILTRO DE EDAD (REGLA MENORES DE 6 AÑOS)
    # Busca frases como "3 años", "4 años", "5 añitos"
    if re.search(r'\b([1-5])\s*(año|ano|añito)', texto):
        mensaje_respuesta = respuestas.MENSAJES["menores_6_anios"] + respuestas.FIRMA_DINAMICA
        # Aquí enviaríamos la foto de Personalizadas y el mensaje_respuesta
        return "Filtro de edad aplicado"

    # 4. BUSCADOR INTELIGENTE EN EL CATÁLOGO (FUZZY MATCHING)
    # Creamos una lista plana con todas las palabras clave del catálogo
    todas_palabras = []
    for key, data in menu_imagenes.CATALOGO_IMAGENES.items():
        todas_palabras.extend(data["palabras_clave"])
    
    # Comparamos lo que escribió el usuario con nuestras palabras clave
    mejor_coincidencia = process.extractOne(texto, todas_palabras)
    
    if mejor_coincidencia and mejor_coincidencia[1] >= 85: # 85% de similitud mínima (tolera faltas de ortografía)
        palabra_encontrada = mejor_coincidencia[0]
        # Aquí buscaríamos a qué ID pertenece esa palabra, elegiríamos un texto aleatorio y enviaríamos la(s) foto(s)
        return f"Catálogo enviado por coincidencia con: {palabra_encontrada}"
        
    # 5. MENSAJE POR DEFECTO (NO ENTENDIÓ)
    # Aquí enviaríamos respuestas.MENSAJES["no_entiendo"]
    return "Mensaje no entendido"

# ==========================================
# 🌐 CONEXIÓN CON WHATSAPP (WEBHOOK)
# ==========================================
@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    if request.method == "GET":
        # Meta verifica que somos nosotros
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Token de verificación inválido", 403
        
    elif request.method == "POST":
        # Recibimos un mensaje nuevo
        datos = request.json
        try:
            # Extraemos los datos del JSON que manda Meta
            mensaje_data = datos["entry"][0]["changes"][0]["value"]["messages"][0]
            telefono = datos["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
            
            if "text" in mensaje_data:
                texto = mensaje_data["text"]["body"]
                procesar_mensaje(telefono, texto)
                
        except (KeyError, IndexError):
            pass # Ignoramos eventos de Meta que no sean mensajes (como "mensaje leído")
            
        return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)