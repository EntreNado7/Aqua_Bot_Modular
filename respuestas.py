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

# ==========================================
# ARCHIVO: respuestas.py
# FUNCIÓN: Almacena los textos de respuesta y descripciones.
# ==========================================

MENSAJES = {
    "bienvenida_nueva": "¡Hola! Qué gusto saludarte. Soy Aqua, tu asistente virtual en EntreNado. 🌊\nPara darte la mejor atención, elige una de las siguientes opciones:",
    "traspaso_horario_habil": "Con mucho gusto. 🧑‍💻 En un momento uno de nuestros asesores revisará tu caso para atenderte personalmente. ¡Gracias por tu paciencia!",
    "no_entiendo": "No estoy muy segura de a qué te refieres 🤔. ¿Podrías escribirlo de otra forma o elegir una de las opciones del menú?",
    "ubicacion": "📍 Nos encontramos en: [Tu Dirección, Ciudad].\n\nPuedes abrir el mapa directamente aquí para llegar fácilmente:\nhttps://maps.app.goo.gl/qs2oLbgv2oGoSncD7",
    "horarios": "🕒 Nuestras puertas están abiertas para recibirte en los siguientes horarios:\n\n🔸 Lunes a Viernes: 6:00 a 21:00 hrs.\n🔸 Sábados: 7:00 a 14:00 hrs.",
    "menu_clases": "En EntreNado tenemos opciones para todas las edades y objetivos. 💪\nElige qué mundo te gustaría explorar o conoce cómo combinarlos:",
    "menu_agua": "El agua es nuestro elemento. 💙 Tenemos programas especializados para cada etapa.\n¿Para quién buscas información?",
    "menu_adultos": "¡Excelente! Para adultos contamos con:\n\n🔸 *Grupales:* Clases por niveles para aprender o perfeccionar técnica.\n🔸 *Nado Libre:* Entrena a tu ritmo en carriles exclusivos.\n🔸 *Aquafitness:* Ejercicio funcional de bajo impacto con música.\n🔸 *Rehabilitación:* Terapia acuática personalizada.\n\n✏️ *Por favor, escribe la clase que más te interesa para darte los detalles.*",
    "menu_infantiles": "¡Los más pequeños son nuestra especialidad! 🐬 Para niños y jóvenes tenemos:\n\n🔸 *Grupales (Escolares):* Aprendizaje por niveles y convivencia.\n🔸 *Personalizadas:* Atención 1 a 1 para un avance a su medida.\n\n✏️ *Por favor, escribe cuál de estas dos opciones te interesa explorar.*"
}

DESCRIPCIONES = {
    "bebes": ("👶 *Natación para Bebés*\nSon sesiones personalizadas de 30 minutos. De la mano de un instructor especializado, tu bebé desarrollará habilidades de supervivencia, estimulación temprana y confianza en el agua, todo en un ambiente seguro y cálido. 💙\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Bebés", "🗣️ Asesor"]),
    
    "aquafitness": ("💦 *Aquafitness*\n¡La forma más divertida de ejercitarse! Es un entrenamiento funcional bajo el agua que protege tus articulaciones mientras quemas calorías al ritmo de la música. Ideal para mejorar tu condición física sin impacto.\n\n¿Te comparto la imagen con los costos o prefieres hablar con un asesor?", ["💲 Costos Aquafit", "🗣️ Asesor"]),
    
    "nado libre": ("🏊‍♂️ *Nado Libre*\nPerfecto si ya dominas la técnica y buscas un espacio para entrenar a tu propio ritmo. Te asignamos un carril para que disfrutes de tu rutina con total libertad.\n\n¿Te gustaría conocer la inversión o prefieres que un humano te apoye?", ["💲 Costos N. Libre", "🗣️ Asesor"]),
    
    "grupales adultos": ("🧑 *Clases Grupales para Adultos*\nNunca es tarde para aprender o mejorar. Nuestras clases están divididas por niveles para que avances a tu propio ritmo acompañado de nuestros instructores.\n\n¿Quieres que te envíe los costos o prefieres hablar con un asesor?", ["💲 Costos Adultos", "🗣️ Asesor"]),
    
    "rehabilitacion": ("🩹 *Rehabilitación Acuática*\nAtención especializada y gentil para tu cuerpo. Usamos las propiedades del agua para ayudarte en tu proceso de recuperación física, aliviando el dolor y mejorando tu movilidad de forma segura.\n\n¿Te comparto los costos o te comunico con recepción?", ["💲 Costos Rehab", "🗣️ Asesor"]),
    
    "grupales infantiles": ("🐬 *Grupales Infantiles (Escolares)*\nGrupos organizados por niveles donde los niños aprenden a nadar de forma divertida y segura. Fomentamos la disciplina, la técnica y el compañerismo.\n\n¿Te envío la imagen con las mensualidades o prefieres hablar con un asesor?", ["💲 Costos Infantiles", "🗣️ Asesor"]),
    
    "personalizadas infantiles": ("⭐ *Clases Infantiles Personalizadas*\nAtención 100% enfocada en tu hijo. Ideal para niños que necesitan superar el miedo al agua, requieren atención especial, o buscan un avance técnico mucho más acelerado.\n\n¿Te gustaría ver los precios o prefieres hablar con recepción?", ["💲 Costos Infantiles", "🗣️ Asesor"])
}
# 3. Firma Dinámica (Pie de mensaje para retención)
FIRMA_DINAMICA = "\n\n¿Te puedo ayudar con algo más? 👇"
