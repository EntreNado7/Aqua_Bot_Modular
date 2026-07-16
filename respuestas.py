# ==========================================
# ARCHIVO: respuestas.py
# FUNCIÓN: Almacenar los textos, menús y enlaces de Aqua.
# ==========================================

# 1. Configuración de Recepción Humana
NUMERO_RECEPCION = "527772596086"
TEXTO_PRELLENADO = "Hola, vengo del asistente virtual. Me gustaría hablar con un asesor para recibir atención humana."

# Codificamos el texto para que las URL lo entiendan (cambia espacios por %20)
import urllib.parse
texto_url = urllib.parse.quote(TEXTO_PRELLENADO)
LINK_RECEPCION = f"https://wa.me/{NUMERO_RECEPCION}?text={texto_url}"

# 2. Diccionario de Mensajes Principales
MENSAJES = {
    # Saludos
    "bienvenida_nueva": "¡Hola! 👋 Soy Aqua, el Asistente Digital del Club Deportivo EntreNado. Veo que es la primera vez que nos escribes, ¡bienvenida(o)! 🌊\n\n¿En qué te puedo ayudar hoy? Elige una opción o escríbeme tu duda:",
    "bienvenida_recurrente": "¡Hola de nuevo, {nombre}! 🌊 Qué gusto saludarte.\n\n¿En qué te puedo apoyar el día de hoy?",
    
    # Filtros Estratégicos
    "filtro_edad": "¡Claro! Para brindarte la información y la modalidad correcta, ¿qué edad tiene el alumno? 👇",
    "filtro_modalidad": "¡Perfecto! Para brindarte la información exacta, ¿te interesan nuestras clases Grupales o prefieres atención Personalizada? 👇",
    
    # Regla de Negocio: Menores de 6 años
    "menores_6_anios": "¡Qué excelente edad para empezar a disfrutar del agua! 🐠 Pensando en el aprendizaje y la seguridad de los peques menores de 6 años, recomendamos nuestras Clases Personalizadas, donde un instructor se enfoca 100% en su desarrollo.",
    
    # Traspaso a Humano (Handoff)
    "traspaso_horario_habil": f"📝 He notificado a nuestra recepción sobre tu solicitud.\n\nPara agilizar tu atención, da clic en el siguiente enlace y déjales un mensaje. Un administrador tomará tu chat enseguida para continuar con tu proceso:\n👉 {LINK_RECEPCION}",
    
    "traspaso_fuera_horario": f"📝 He notificado a nuestra recepción sobre tu solicitud.\n\nTen en cuenta que el horario de respuesta de nuestros asesores es de *Lunes a Viernes de 7:00 AM a 8:00 PM y Sábados de 8:00 AM a 2:00 PM*.\n\nPara agilizar tu atención, da clic en el siguiente enlace y déjales un mensaje. Te responderán por ese medio en cuanto inicie su turno:\n👉 {LINK_RECEPCION}",
    
    # Fallback (Cuando el bot no entiende)
    "no_entiendo": "Disculpa, no logré comprender tu mensaje. 💧 Recuerda que soy un asistente virtual en entrenamiento. ¿Podrías intentar elegir una de las opciones del menú o pedir hablar con un asesor?"
}

# 3. Firma Dinámica (Pie de mensaje para retención)
FIRMA_DINAMICA = "\n\n¿Te puedo ayudar con algo más? 👇"