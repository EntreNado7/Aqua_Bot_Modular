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
import urllib.parse

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
    """Envía texto, imagen, botones interactivos o menús de lista."""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    
    # 1️⃣ CASO: Enviar Botones Interactivos (Si recibe una lista [])
    if botones and isinstance(botones, list):
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
        
    # 1.5️⃣ CASO NUEVO: Enviar Menú de Lista (Si recibe un diccionario {})
    elif botones and isinstance(botones, dict):
        payload = {
            "messaging_product": "whatsapp",
            "to": telefono,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {"type": "text", "text": botones["header"]},
                "body": {"text": texto_respuesta},
                "footer": {"text": botones["footer"]},
                "action": {
                    "button": botones["button_text"],
                    "sections": botones["sections"]
                }
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
# ==========================================
# 🧠 LÓGICA PRINCIPAL DEL CHAT
# ==========================================
def procesar_mensaje(identificador, texto):
    texto = texto.lower().strip()
    
    # 1. VERIFICAR CLIENTE EN NOTION Y OBTENER FECHA
    cliente_id, fecha_ultima = notion_api.verificar_cliente(identificador)
    
    if not cliente_id:
        notion_api.registrar_lead(identificador)
        texto_bienvenida = respuestas.MENSAJES["bienvenida_nueva"]
        mis_botones = ["📍 Ubicación", "🕒 Horarios", "🏊‍♂️ Ver Clases"]
        return texto_bienvenida, None, mis_botones
    else:
        # Siempre actualizamos la fecha del nuevo mensaje
        notion_api.actualizar_interaccion(cliente_id, texto)

    # 1.5 TEMPORIZADOR DE SESIÓN Y SALUDO DINÁMICO
    sesion_nueva = False
    
    if fecha_ultima:
        try:
            # Calculamos cuántas horas han pasado desde el último mensaje
            fecha_obj = datetime.fromisoformat(fecha_ultima.replace('Z', '+00:00')).replace(tzinfo=None)
            diferencia_horas = (datetime.utcnow() - fecha_obj).total_seconds() / 3600
            
            if diferencia_horas > 12: # Si pasaron más de 12 horas, es una nueva sesión
                sesion_nueva = True
        except Exception as e:
            print(f"Error al calcular tiempo: {e}")
            sesion_nueva = False # <--- ¡FIX: No trabamos la sesión si hay error en Notion!
    else:
        sesion_nueva = True 

    # Interceptor de saludos manuales y comandos de reinicio
    saludos_directos = ["hola", "holas", "buenos dias", "buenas tardes", "buenas noches", "menu", "menú", "info", "informacion", "información", "reset", "reiniciar", "inicio"]
    
    # ESCUDO PARA BOTONES: Si presiona un botón del sistema, no reiniciamos el menú.
    botones_sistema = ["📍 ubicación", "ubicación", "ubicacion", "🕒 horarios", "horarios", "🏊‍♂️ ver clases", "ver clases"]
    
    if texto in saludos_directos or (sesion_nueva and texto not in botones_sistema):
        hora_local = datetime.now().hour # Toma la hora exacta de Cuernavaca gracias a la variable de Render
        
        if hora_local < 12:
            saludo = "¡Buenos días!"
        elif hora_local < 19:
            saludo = "¡Buenas tardes!"
        else:
            saludo = "¡Buenas noches!"
            
        texto_bienvenida = f"{saludo} 🌊 Qué gusto tenerte de vuelta.\n¿En qué te puedo ayudar hoy? Elige una opción:"
        mis_botones = ["📍 Ubicación", "🕒 Horarios", "🏊‍♂️ Ver Clases"]
        return texto_bienvenida, None, mis_botones

    # 2. BOTÓN DE ASESOR (HANDOFF)
    if "asesor" in texto or "humano" in texto or "recepcion" in texto:
        notion_api.solicitar_humano(cliente_id)
        
        # 1. Obtenemos el historial de Notion
        historial_bruto = notion_api.obtener_historial(cliente_id)
        resumen = ""
        if historial_bruto:
            # Limpiamos la palabra 'asesor' del final para que el resumen sea sobre las clases
            camino = historial_bruto.replace(" > asesor", "").replace(" > humano", "")
            # Tomamos los últimos 100 caracteres para no romper el link
            resumen = f"\n\n*(Contexto: {camino[-100:]})*"
            
        # 2. Define el número de la recepción de EntreNado
        numero_recepcion = "5217772596086"
        
        # 3. Creamos el mensaje prellenado
        mensaje_base = f"Hola, por favor envía este mensaje para que un asesor continúe con tu atención. 🌊{resumen}"
        import urllib.parse
        mensaje_codificado = urllib.parse.quote(mensaje_base)
        
        # 4. Generamos el link
        link_whatsapp = f"https://wa.me/{numero_recepcion}?text={mensaje_codificado}"
        
        # 5. Respuesta final con la instrucción clara
        texto_handoff = f"¡Claro que sí! 🙋‍♀️ He notificado a nuestro equipo.\n\nPara continuar tu atención de forma personalizada, haz clic en el siguiente enlace y *envía el mensaje* que aparecerá en tu pantalla:\n👉 {link_whatsapp}"
        
        return texto_handoff, None, None

    # 3. INTERACCIONES DE MENÚ PRINCIPAL (Botones Fijos)
    if texto in ["📍 ubicación", "ubicación", "ubicacion"]:
        return respuestas.MENSAJES["ubicacion"], None, None
    elif texto in ["🕒 horarios", "horarios"]:
        return respuestas.MENSAJES["horarios"], None, None
    elif texto in ["🏊‍♂️ ver clases", "ver clases"]:
        # NUEVA IDENTIDAD VISUAL: ÷Agua y ÷Tierra
        return respuestas.MENSAJES["menu_clases"], None, ["💦 Clases ÷Agua", "🌍 Clases ÷Tierra", "🎁 Paquetes Combo"]
    
    # 3.1 BIFURCACIONES DEL MENÚ DE AGUA
    elif texto in ["💦 clases ÷agua", "clases ÷agua", "clases de agua", "agua"]:
        return respuestas.MENSAJES["menu_agua"], None, ["🧑 Adultos", "👧 Infantiles/Juv", "👶 Bebés"]
        
    elif texto in ["🧑 adultos", "adultos"]:
        return respuestas.MENSAJES["menu_adultos"], None, None
        
    elif texto in ["👧 infantiles/juv", "infantiles/juv", "infantiles", "juveniles"]:
        return respuestas.MENSAJES["menu_infantiles"], None, None

    elif texto in ["mamá & bebé", "mama & bebe", "mamá y bebé", "mama y bebe", "mama", "mamá"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["mama y bebe"]
        return desc_texto, None, desc_botones
        
    elif texto in ["👶 bebés", "bebes"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["bebes"]
        return desc_texto, None, desc_botones
        
    # 3.2 BIFURCACIONES DEL MENÚ DE TIERRA
    elif texto in ["🌍 clases ÷tierra", "clases ÷tierra", "clases de tierra", "tierra"]:
        botones_tierra = ["💪 Clases Fitness", "🥊 Box", "🏋️‍♂️ Open Gym"]
        return respuestas.MENSAJES["menu_tierra"], None, botones_tierra
        
    elif texto in ["💪 clases fitness", "clases fitness", "fitness", "multidisciplina"]:
        # AQUÍ DISPARAMOS EL NUEVO MENÚ DE LISTA DE FITNESS
        return respuestas.TEXTO_FITNESS, None, respuestas.LISTA_FITNESS
        
    elif texto in ["🥊 box", "box", "escuela de box", "boxeo"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["box"]
        return desc_texto, None, desc_botones
        
    elif texto in ["🏋️‍♂️ open gym", "open gym", "gym", "gimnasio", "uso libre", "open"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["open gym"]
        return desc_texto, None, desc_botones

    # 4. FASE DE CIERRE PRIORITARIO (Si detectamos que el usuario quiere precios)
    if "costo" in texto or "precio" in texto or "💲" in texto or "mensualidad" in texto:
        mapeo_imagenes = {}
        for categoria, datos in menu_imagenes.CATALOGO_IMAGENES.items():
            for keyword in datos["palabras_clave"]:
                mapeo_imagenes[keyword] = categoria
                
        opciones_img = list(mapeo_imagenes.keys())
        coincidencia_img, puntaje_img = process.extractOne(texto, opciones_img)
        
        if puntaje_img >= 65:
            import random
            categoria_encontrada = mapeo_imagenes[coincidencia_img]
            datos_categoria = menu_imagenes.CATALOGO_IMAGENES[categoria_encontrada]
            texto_elegido = random.choice(datos_categoria["textos"])
            imagen_elegida = datos_categoria["links"][0] if datos_categoria["links"] else None
            return texto_elegido, imagen_elegida, None

    # 5. FASE DE EXPLORACIÓN: Búsqueda de Descripciones (Texto Libre)
    opciones_descripciones = list(respuestas.DESCRIPCIONES.keys())
    coincidencia_desc, puntaje_desc = process.extractOne(texto, opciones_descripciones)
    
    if puntaje_desc >= 75:
        # Extraemos el texto y los botones dinámicos desde el diccionario
        texto_descripcion, botones_cierre = respuestas.DESCRIPCIONES[coincidencia_desc]
        return texto_descripcion, None, botones_cierre

    # 6. FASE DE CIERRE SECUNDARIO: Imágenes para palabras generales (ej. "paquetes")
    mapeo_imagenes_secundario = {}
    for categoria, datos in menu_imagenes.CATALOGO_IMAGENES.items():
        for keyword in datos["palabras_clave"]:
            mapeo_imagenes_secundario[keyword] = categoria
            
    opciones_img_sec = list(mapeo_imagenes_secundario.keys())
    coincidencia_img_sec, puntaje_img_sec = process.extractOne(texto, opciones_img_sec)
    
    if puntaje_img_sec >= 65:
        import random
        categoria_encontrada = mapeo_imagenes_secundario[coincidencia_img_sec]
        datos_categoria = menu_imagenes.CATALOGO_IMAGENES[categoria_encontrada]
        texto_elegido = random.choice(datos_categoria["textos"])
        imagen_elegida = datos_categoria["links"][0] if datos_categoria["links"] else None
        return texto_elegido, imagen_elegida, None

    # 7. MENSAJE POR DEFECTO (Fallback)
    return respuestas.MENSAJES["no_entiendo"], None, None

# 2. BOTÓN DE ASESOR (HANDOFF)
    if "asesor" in texto or "humano" in texto or "recepcion" in texto:
        notion_api.solicitar_humano(cliente_id)
        
        # 1. Obtenemos el historial de Notion
        historial_bruto = notion_api.obtener_historial(cliente_id)
        resumen = ""
        if historial_bruto:
            # Limpiamos la palabra 'asesor' del final para que el resumen sea sobre las clases
            camino = historial_bruto.replace(" > asesor", "").replace(" > humano", "")
            # Tomamos los últimos 100 caracteres para no romper el link
            resumen = f"\n\n*(Contexto: {camino[-100:]})*"
            
        # 2. Define el número de la recepción de EntreNado
        numero_recepcion = "5217772596086"
        
        # 3. Creamos el mensaje prellenado
        mensaje_base = f"Hola, por favor envía este mensaje para que un asesor continúe con tu atención. 🌊{resumen}"
        import urllib.parse
        mensaje_codificado = urllib.parse.quote(mensaje_base)
        
        # 4. Generamos el link
        link_whatsapp = f"https://wa.me/{numero_recepcion}?text={mensaje_codificado}"
        
        # 5. Respuesta final con la instrucción clara
        texto_handoff = f"¡Claro que sí! 🙋‍♀️ He notificado a nuestro equipo.\n\nPara continuar tu atención de forma personalizada, haz clic en el siguiente enlace y *envía el mensaje* que aparecerá en tu pantalla:\n👉 {link_whatsapp}"
        
        return texto_handoff, None, None

    # 3. INTERACCIONES DE MENÚ PRINCIPAL (Botones Fijos)
    if texto in ["📍 ubicación", "ubicación", "ubicacion"]:
        return respuestas.MENSAJES["ubicacion"], None, None
    elif texto in ["🕒 horarios", "horarios"]:
        return respuestas.MENSAJES["horarios"], None, None
    elif texto in ["🏊‍♂️ ver clases", "ver clases"]:
        return respuestas.MENSAJES["menu_clases"], None, ["💦 Clases de Agua", "🌍 Clases de Tierra", "🎁 Paquetes Combo"]
    
# 3.1 BIFURCACIONES DEL MENÚ DE AGUA
    elif texto in ["💦 clases de agua", "clases de agua", "agua"]:
        # Aquí actualizamos el nombre del botón
        return respuestas.MENSAJES["menu_agua"], None, ["🧑 Adultos", "👧 Infantiles/Juv", "👶 Bebés"]
        
    elif texto in ["🧑 adultos", "adultos"]:
        return respuestas.MENSAJES["menu_adultos"], None, None
        
    # Agregamos las nuevas palabras clave para detectar el botón modificado
    elif texto in ["👧 infantiles/juv", "infantiles/juv", "infantiles", "juveniles"]:
        return respuestas.MENSAJES["menu_infantiles"], None, None

    # --- NUEVO ATAJO PARA MAMÁ & BEBÉ ---
    elif texto in ["mamá & bebé", "mama & bebe", "mamá y bebé", "mama y bebe", "mama", "mamá"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["mama y bebe"]
        return desc_texto, None, desc_botones

    
    elif texto in ["👶 bebés", "bebes"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["bebes"]
        return desc_texto, None, desc_botones
        
# 3.2 BIFURCACIONES DEL MENÚ DE TIERRA
    elif texto in ["🌍 clases de tierra", "clases de tierra", "tierra"]:
        botones_tierra = ["💪 Clases Fitness", "🥊 Box", "🏋️‍♂️ Open Gym"]
        return respuestas.MENSAJES["menu_tierra"], None, botones_tierra
        
    elif texto in ["💪 clases fitness", "clases fitness", "fitness", "multidisciplina"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["clases fitness"]
        return desc_texto, None, desc_botones
        
    elif texto in ["🥊 box", "box", "escuela de box", "boxeo"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["box"]
        return desc_texto, None, desc_botones
        
    elif texto in ["🏋️‍♂️ open gym", "open gym", "gym", "gimnasio", "uso libre", "open"]:
        desc_texto, desc_botones = respuestas.DESCRIPCIONES["open gym"]
        return desc_texto, None, desc_botones

   # 4. FASE DE CIERRE PRIORITARIO (Si detectamos que el usuario quiere precios)
    if "costo" in texto or "precio" in texto or "💲" in texto or "mensualidad" in texto:
        mapeo_imagenes = {}
        for categoria, datos in menu_imagenes.CATALOGO_IMAGENES.items():
            for keyword in datos["palabras_clave"]:
                mapeo_imagenes[keyword] = categoria
                
        opciones_img = list(mapeo_imagenes.keys())
        coincidencia_img, puntaje_img = process.extractOne(texto, opciones_img)
        
        if puntaje_img >= 65:
            import random
            categoria_encontrada = mapeo_imagenes[coincidencia_img]
            datos_categoria = menu_imagenes.CATALOGO_IMAGENES[categoria_encontrada]
            texto_elegido = random.choice(datos_categoria["textos"])
            imagen_elegida = datos_categoria["links"][0] if datos_categoria["links"] else None
            return texto_elegido, imagen_elegida, None

    # 5. FASE DE EXPLORACIÓN: Búsqueda de Descripciones (Texto Libre)
    opciones_descripciones = list(respuestas.DESCRIPCIONES.keys())
    coincidencia_desc, puntaje_desc = process.extractOne(texto, opciones_descripciones)
    
    if puntaje_desc >= 75:
        # Extraemos el texto y los botones dinámicos desde el diccionario
        texto_descripcion, botones_cierre = respuestas.DESCRIPCIONES[coincidencia_desc]
        return texto_descripcion, None, botones_cierre

    # 6. FASE DE CIERRE SECUNDARIO: Imágenes para palabras generales (ej. "paquetes")
    mapeo_imagenes_secundario = {}
    for categoria, datos in menu_imagenes.CATALOGO_IMAGENES.items():
        for keyword in datos["palabras_clave"]:
            mapeo_imagenes_secundario[keyword] = categoria
            
    opciones_img_sec = list(mapeo_imagenes_secundario.keys())
    coincidencia_img_sec, puntaje_img_sec = process.extractOne(texto, opciones_img_sec)
    
    if puntaje_img_sec >= 65:
        import random
        categoria_encontrada = mapeo_imagenes_secundario[coincidencia_img_sec]
        datos_categoria = menu_imagenes.CATALOGO_IMAGENES[categoria_encontrada]
        texto_elegido = random.choice(datos_categoria["textos"])
        imagen_elegida = datos_categoria["links"][0] if datos_categoria["links"] else None
        return texto_elegido, imagen_elegida, None

    # 7. MENSAJE POR DEFECTO (Fallback)
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
                            
                            # --- EXTRAEMOS EL TEXTO (NUEVO OÍDO PARA LISTAS) ---
                            if "interactive" in mensaje_data:
                                if "button_reply" in mensaje_data["interactive"]:
                                    texto = mensaje_data["interactive"]["button_reply"]["title"]
                                elif "list_reply" in mensaje_data["interactive"]:
                                    texto = mensaje_data["interactive"]["list_reply"]["title"]
                            else:
                                texto = mensaje_data["text"]["body"]
                            # ---------------------------------------------------
                            
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
