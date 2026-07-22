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
    # --- DENTRO DEL DICCIONARIO 'MENSAJES' ---

    "menu_adultos": "¡Excelente! Para adultos contamos con:\n\n🔹 *Grupales:* Clases por niveles para aprender o perfeccionar técnica.\n🔹 *Personalizadas:* Atención 1 a 1 enfocada en tus objetivos.\n🔹 *Mamá & Bebé:* Clase grupal para ti, en compañía de tu pequeño.\n🔹 *Nado Libre:* Entrena a tu ritmo en carriles exclusivos.\n🔹 *Aquafitness:* Ejercicio funcional de bajo impacto con música.\n🔹 *Rehabilitación:* Terapia acuática personalizada.\n\n✏️ *Por favor, escribe la clase que más te interesa para darte los detalles.*",
    
    "menu_infantiles": "¡Los más pequeños y jóvenes son nuestra especialidad! 🐬 Para edades de *4 a 17 años* tenemos:\n\n🔹 *Grupales (Escolares):* Aprendizaje por niveles y convivencia.\n🔹 *Personalizadas:* Atención 1 a 1 para un avance a su medida.\n\n✏️ *Por favor, escribe cuál de estas dos opciones te interesa explorar.*",
   "menu_tierra": "¡Excelente! Para entrenar en piso contamos con tres modalidades principales:\n\n🔹 *Clases Fitness (Multidisciplina):* Paquete flexible para combinar Yoga, Spinning, Funcional, GAP, entre otras.\n🔹 *Box (Especialidad):* Entrenamiento exclusivo enfocado en técnica y combate (¡A partir de los 6 años!).\n🔹 *Open Gym:* Uso libre de nuestras instalaciones para entrenar a tu propio ritmo.\n\n👇 *Por favor, haz clic en la opción que te interesa para darte los detalles:*",
}

DESCRIPCIONES = {
    "bebes": ("👶 *Natación para Bebés*\nSon sesiones personalizadas de 30 minutos. De la mano de un instructor especializado, tu bebé desarrollará habilidades de supervivencia, estimulación temprana y confianza en el agua, todo en un ambiente seguro y cálido. 💙\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Bebés", "🗣️ Asesor"]),
    
    "aquafitness": ("💦 *Aquafitness*\n¡La forma más divertida de ejercitarse! Es un entrenamiento funcional bajo el agua que protege tus articulaciones mientras quemas calorías al ritmo de la música. Ideal para mejorar tu condición física sin impacto.\n\n¿Te comparto la imagen con los costos o prefieres hablar con un asesor?", ["💲 Costos Aquafit", "🗣️ Asesor"]),
    
    "nado libre": ("🏊‍♂️ *Nado Libre*\nPerfecto si ya dominas la técnica y buscas un espacio para entrenar a tu propio ritmo. Te asignamos un carril para que disfrutes de tu rutina con total libertad.\n\n¿Te gustaría conocer la inversión o prefieres que un humano te apoye?", ["💲 Costos N. Libre", "🗣️ Asesor"]),
    
    # --- DENTRO DEL DICCIONARIO 'DESCRIPCIONES' (Agrega estas dos nuevas) ---

    "personalizadas adultos": ("⭐ *Clases Personalizadas para Adultos*\nAtención exclusiva 1 a 1. Ideal para superar el miedo al agua, entrenar para un evento específico o avanzar a tu propio ritmo con un instructor dedicado 100% a ti.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Personal", "🗣️ Asesor"]),
    
    "mama y bebe": ("👩‍👦 *Mamá & Bebé (Clase Grupal)*\n¡Un espacio diseñado para ti, mamá! En esta clase grupal tú eres la alumna principal. Te ejercitarás, convivirás con otras mamás y disfrutarás del agua mientras tu bebé te acompaña en esta hermosa etapa de conexión.\n\n¿Te comparto la imagen con los costos o prefieres hablar con un asesor?", ["💲 Costos Mamá Bebé", "🗣️ Asesor"]),
    
    "rehabilitacion": ("🩹 *Rehabilitación Acuática*\nAtención especializada y gentil para tu cuerpo. Usamos las propiedades del agua para ayudarte en tu proceso de recuperación física, aliviando el dolor y mejorando tu movilidad de forma segura.\n\n¿Te comparto los costos o te comunico con recepción?", ["💲 Costos Rehab", "🗣️ Asesor"]),
    
    "grupales infantiles": ("🐬 *Grupales Infantiles (Escolares)*\nGrupos organizados por niveles donde los niños aprenden a nadar de forma divertida y segura. Fomentamos la disciplina, la técnica y el compañerismo.\n\n¿Te envío la imagen con las mensualidades o prefieres hablar con un asesor?", ["💲 Costos Infantiles", "🗣️ Asesor"]),
    
    "personalizadas infantiles": ("⭐ *Clases Infantiles Personalizadas*\nAtención 100% enfocada en tu hijo. Ideal para niños que necesitan superar el miedo al agua, requieren atención especial, o buscan un avance técnico mucho más acelerado.\n\n¿Te gustaría ver los precios o prefieres hablar con recepción?", ["💲 Costos Infantiles", "🗣️ Asesor"]),
    "clases fitness": ("💪 *Clases Fitness (Multidisciplina)*\nContamos con 8 disciplinas diseñadas para fortalecer tu cuerpo y mejorar tu condición física:\n_Spinning, Yoga, GAP, Entrenamiento Funcional, FitDance, Senior's Health, Full Power y Optimove._\n\n¿Te gustaría ver nuestra tabla de costos y descubrir cómo puedes combinarlas, o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),

    "box": ("🥊 *Box (Especialidad)*\n¡Libera la tensión, gana agilidad y mejora tu condición física al máximo! Nuestro entrenamiento exclusivo de Box te enseñará técnica de golpeo, combinaciones y desplazamientos en sesiones de alta intensidad.\n\n👦👧 *¡Apto a partir de los 6 años!* Es ideal tanto para niños y jóvenes que buscan canalizar su energía y ganar disciplina, como para adultos que desean un entrenamiento explosivo.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Box", "🗣️ Asesor"]),

    "open gym": ("🏋️‍♂️ *Open Gym*\nPara quienes ya tienen su propia rutina y solo necesitan el espacio adecuado. Disfruta del uso libre de nuestras instalaciones y equipo para entrenar a tu propio ritmo y bajo tus propias reglas.\n\n⚠️ _Nota importante:_ Esta modalidad es de entrenamiento autónomo (sin supervisión de un instructor) y aplica únicamente dentro de horarios específicos preestablecidos.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Open Gym", "🗣️ Asesor"]),
    "spinning": ("🚴 *Spinning*\n¡Sube la energía y quema calorías al máximo! Una clase de cardio intenso sobre bicicleta estacionaria, guiada por el ritmo de la música. Ideal para fortalecer tus piernas, mejorar tu resistencia cardiovascular y liberar estrés.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),

    "yoga": ("🧘 *Yoga*\nEncuentra el equilibrio perfecto entre cuerpo y mente. A través de posturas guiadas y control de la respiración, mejorarás tu flexibilidad, fuerza, postura y lograrás una relajación profunda. Ideal para todos los niveles.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),

    "gap": ("🍑 *GAP (Glúteo, Abdomen y Pierna)*\nUn entrenamiento enfocado y directo al grano. Esta clase está diseñada específicamente para tonificar, fortalecer y definir tu tren inferior y tu zona core a través de ejercicios muy localizados.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),

    "funcional": ("💪 *Entrenamiento Funcional*\nPrepara tu cuerpo para el día a día. Utilizando tu propio peso y herramientas dinámicas, realizarás ejercicios que involucran varios grupos musculares al mismo tiempo. Ganarás fuerza, resistencia, velocidad y coordinación.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),

    "fitdance": ("💃 *FitDance*\n¡Hacer ejercicio nunca fue tan divertido! Una clase llena de ritmo donde quemarás calorías mientras bailas coreografías dinámicas y fáciles de seguir. No necesitas saber bailar, ¡solo tener ganas de moverte y sudar!\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),

    "senior health": ("👵 *Senior's Health*\nMovimiento seguro y diseñado especialmente para adultos mayores. Una clase de bajo impacto enfocada en mantener y mejorar la movilidad articular, la fuerza, el equilibrio y la calidad de vida, todo en un ambiente cuidadoso y adaptado.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),

    "full power": ("⚡ *Full Power*\n¡Lleva tu cuerpo al siguiente nivel! Un entrenamiento explosivo de alta intensidad diseñado para aquellos que buscan superar sus límites. Desarrollarás máxima fuerza, potencia y resistencia muscular en una sesión retadora.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),

    "optimove": ("🔄 *Optimove*\nEntrena con inteligencia. Una clase enfocada en la biomecánica, la corrección postural y la movilidad articular. Ideal para recuperarte activamente, prevenir lesiones y optimizar la forma en que tu cuerpo se mueve todos los días.\n\n¿Te gustaría ver nuestra tabla de costos o prefieres hablar con un asesor?", ["💲 Costos Fitness", "🗣️ Asesor"]),
}
# 3. Firma Dinámica (Pie de mensaje para retención)
FIRMA_DINAMICA = "\n\n¿Te puedo ayudar con algo más? 👇"



# ==========================================
# MENÚS DE LISTA (NUEVA FUNCIÓN)
# ==========================================
TEXTO_FITNESS = "💪 *Clases Fitness (Multidisciplina)*\nContamos con 8 disciplinas diseñadas para fortalecer tu cuerpo y mejorar tu condición física.\n\n👇 *Toca el botón de abajo para descubrir de qué trata cada una y encontrar tu favorita.*"

LISTA_FITNESS = {
    "header": "Disciplinas Fitness 🏊‍♂️",
    "button_text": "📋 Elegir Disciplina",
    "footer": "Club Deportivo EntreNado",
    "sections": [
        {
            "title": "Clases Disponibles",
            "rows": [
                {"id": "f_spin", "title": "🚴 Spinning", "description": "Cardio intenso en bicicleta"},
                {"id": "f_yoga", "title": "🧘 Yoga", "description": "Flexibilidad, fuerza y postura"},
                {"id": "f_gap", "title": "🍑 GAP", "description": "Glúteo, Abdomen y Pierna"},
                {"id": "f_func", "title": "💪 Funcional", "description": "Fuerza y resistencia total"},
                {"id": "f_dance", "title": "💃 FitDance", "description": "Quema calorías bailando"},
                {"id": "f_sen", "title": "👵 Senior Health", "description": "Movimiento seguro sin impacto"},
                {"id": "f_power", "title": "⚡ Full Power", "description": "Fuerza y potencia al máximo"},
                {"id": "f_opti", "title": "🔄 Optimove", "description": "Biomecánica y movilidad articular"}
            ]
        }
    ]
}

# ==========================================
# MENÚS DE LISTA PARA AGUA (DIVIDIDOS)
# ==========================================
TEXTO_ADULTOS = "🧑 *Clases para Adultos y Especialidades*\nContamos con opciones para que entrenes, te relajes o te recuperes a tu propio ritmo. 💧\n\n👇 *Toca el botón de abajo para explorar nuestras clases.*"

LISTA_ADULTOS = {
    "header": "Adultos y Especialidades",
    "button_text": "📋 Elegir Clase",
    "footer": "Club Deportivo EntreNado",
    "sections": [
        {
            "title": "Opciones Disponibles",
            "rows": [
                {"id": "a_nado", "title": "🏊‍♂️ Nado Libre", "description": "Entrena a tu propio ritmo"},
                {"id": "a_aqua", "title": "💦 Aquafitness", "description": "Cardio divertido sin impacto"},
                {"id": "a_ad_pers", "title": "⭐ Adultos Personal", "description": "Clase exclusiva 1 a 1"},
                {"id": "a_mama", "title": "👩‍👦 Mamá & Bebé", "description": "Ejercicio y conexión en el agua"},
                {"id": "a_rehab", "title": "🩹 Rehabilitación", "description": "Recuperación física acuática"}
            ]
        }
    ]
}

TEXTO_INFANTILES = "👧👦 *Clases Infantiles y Juveniles*\nProgramas seguros y divertidos para que los más pequeños aprendan a nadar y mejoren su técnica. 🐬\n\n👇 *Toca el botón de abajo para ver las opciones.*"

LISTA_INFANTILES = {
    "header": "Infantiles y Juveniles",
    "button_text": "📋 Elegir Clase",
    "footer": "Club Deportivo EntreNado",
    "sections": [
        {
            "title": "Opciones Disponibles",
            "rows": [
                {"id": "a_inf_grup", "title": "🐬 Grupales Infantiles", "description": "Aprendizaje seguro por niveles"},
                {"id": "a_inf_pers", "title": "⭐ Infantiles Personal", "description": "Atención exclusiva 1 a 1"}
            ]
        }
    ]
}



