# -*- coding: utf-8 -*-
"""
Contenido inicial: el caso "generic" (RecommendationCase) y sus 27 textos
(planilla "Recomendaciones Optimizadas", perfil "5. Genérico", columna
Recomendacion_Optimizada), 3 gráficos x 9 combinaciones de niveles.

Se carga una sola vez; desde ahí la fuente de verdad es la base de datos y
los textos se editan en el admin. Sólo crea los que faltan: nunca pisa un
texto ya editado.
"""

from django.db import migrations

LOW, MID, HIGH = 'low', 'mid', 'high'

# (gráfico, nivel de la 1ª métrica, nivel de la 2ª métrica, texto)
INITIAL_TEXTS = [
    # ------------------------------------------------------------------
    # Evaluaciones: E1 = tiempo en la sub-sección de evaluación, E2 = calificación
    # ------------------------------------------------------------------
    ('evaluations', LOW, LOW, """El sistema registra que tanto el tiempo dedicado a esta evaluación (E1) como la calificación obtenida (E2) se ubican por debajo del percentil 33 de tu curso. ¡No te desanimes! Identificar esta situación es el primer paso para ajustar tu estrategia y mejorar tus resultados.

Para organizar mejor tu tiempo y afrontar tus próximas evaluaciones con mayor confianza, te sugerimos:
1. Planificar tu tiempo antes de comenzar la evaluación, distribuyendo los minutos disponibles entre las distintas secciones y reservando un bloque final para revisar.
2. Verificar que comprendes bien el enunciado de cada pregunta antes de responder y releer tus respuestas para confirmar que reflejan tu razonamiento.
3. Acudir al equipo docente, solicitar apoyo a tus compañeros/as o consultar los servicios estudiantiles de la facultad para orientar tu estudio.

¿Consideras que el tiempo dedicado hasta ahora ha sido suficiente para preparar tus evaluaciones o sientes que necesitas un nuevo plan de estudio?

¡Reconocer las dificultades a tiempo te permitirá reorganizar tu camino y alcanzar los objetivos que te propongas!"""),

    ('evaluations', MID, LOW, """El sistema registra que el tiempo invertido en la evaluación (E1) se encuentra en la mediana del curso (entre el percentil 33 y 66), mientras que tu calificación (E2) está por debajo del percentil 33.

Para convertir ese tiempo de dedicación en aprendizajes sólidos y mejores calificaciones, te sugerimos:
1. Detener la lectura lineal y elaborar un mapa conceptual, esquema o resumen con tus propias palabras por cada tema revisado.
2. Resolver de forma manual al menos dos ejercicios prácticos del mismo nivel de dificultad antes de rendir la siguiente evaluación.
3. Consultar activamente tus dudas con docentes o compañeros/as cuando identifiques contenidos que resulten difíciles de comprender.

¿Qué técnicas o formas de estudio utilizas actualmente al preparar un tema y cómo sientes que te ayudan al momento de responder?

¡Dedicar tiempo a descubrir tu mejor manera de aprender es una inversión valiosa para alcanzar tus metas académicas!"""),

    ('evaluations', MID, HIGH, """El sistema registra que el tiempo dedicado a la evaluación (E1) se ubica en la mediana de tu curso (entre el percentil 33 y 66) y tu calificación (E2) supera el percentil 66. ¡Felicitaciones por este excelente resultado!

Para consolidar los hábitos que te dieron éxito y mantener este gran desempeño en las próximas unidades, te sugerimos:
1. Registrar por escrito las dos técnicas de preparación específicas que mejor te funcionaron en esta oportunidad.
2. Aplicar de forma intencionada esas mismas estrategias en la siguiente subunidad, asegurándote de contrastar tus conclusiones con el material oficial.
3. Compartir tus métodos o estudiar con otros/as compañeros/as para reforzar la comprensión profunda de los temas.

¿Qué estrategias específicas de preparación utilizaste en esta ocasión que consideras marcaron la diferencia en tu rendimiento?

¡Confía en tu capacidad; reflexionar sobre lo que te funciona bien te permitirá sostener tus logros a lo largo del curso!"""),

    ('evaluations', HIGH, HIGH, """El sistema registra que tanto el tiempo dedicado a la evaluación (E1) como tu calificación (E2) se ubican por sobre el percentil 66 de tu curso. ¡Muy buen trabajo, vas por un excelente camino!

Para optimizar tus bloques de estudio y cuidar la sostenibilidad de tu rendimiento sin desgaste innecesario, te sugerimos:
1. Dividir las unidades más extensas en metas operativas más pequeñas y concretas antes de comenzar a estudiar.
2. Establecer descansos obligatorios periódicos al completar cada tarea propuesta para mantener la concentración y energía.
3. Evaluar si todo el tiempo invertido fue realmente necesario o si puedes agilizar tus revisiones manteniendo la misma calidad de respuestas.

¿Qué aspectos de tu planificación te permitirían gestionar tu tiempo de forma más ágil sin descuidar la calidad de tu aprendizaje?

¡Reconocer tus logros y balancear el esfuerzo con descansos adecuados te asegurará un aprendizaje sostenible en el tiempo!"""),

    ('evaluations', HIGH, LOW, """El sistema registra que el tiempo dedicado a esta evaluación (E1) supera el percentil 66 de tu curso, pero tu calificación (E2) se halla por debajo del percentil 33. ¡No te desanimes! Estamos aquí para ayudarte a reorientar todo ese esfuerzo.

Para transformar tu tiempo de dedicación en un mejor rendimiento académico, te sugerimos:
1. Elaborar un cronograma semanal comenzando a estudiar por los contenidos más sencillos para construir aprendizajes progresivos hacia lo más complejo.
2. Diseñar resúmenes y esquemas con tus propias palabras para identificar y afianzar los conceptos clave de la materia.
3. Establecer bloques de trabajo enfocado sin distractores ni dispositivos electrónicos cercanos, y solicitar orientación al equipo docente sobre autorregulación.

¿En qué etapas del estudio o de la evaluación sientes que se presentan las mayores dudas o distracciones?

¡Detectar las dificultades es el primer paso indispensable para ajustar tus estrategias y avanzar con éxito!"""),

    ('evaluations', LOW, HIGH, """El sistema registra que tu calificación en la evaluación (E2) se sitúa por sobre el percentil 66 de tu curso, habiendo invertido un tiempo (E1) por debajo del percentil 33. ¡Felicitaciones por lograr este resultado!

Para asegurar que esta efectividad se mantenga a medida que los contenidos del curso ganen en extensión y complejidad, te sugerimos:
1. Poner a prueba tu comprensión explicando a un/a compañero/a los fundamentos conceptuales que justifican tus respuestas correctas.
2. Dedicar entre 15 y 20 minutos adicionales en la próxima subsección a resolver un problema de desarrollo que altere el contexto de las fórmulas planteadas.
3. Si trabajas habitualmente de forma offline, verificar que tus estrategias se adapten bien a la profundidad que exigirán los módulos siguientes.

¿De qué manera podrías confirmar que tus estrategias actuales funcionarán igual de bien ante problemas más complejos?

¡Vas por un excelente camino; afianzar las bases teóricas ahora te dará total tranquilidad para los desafíos futuros!"""),

    ('evaluations', HIGH, MID, """El sistema registra que el tiempo invertido en la evaluación (E1) supera el percentil 66 de tu curso, mientras que tu calificación (E2) se ubica en la mediana (entre el percentil 33 y 66). ¡Tu dedicación es muy valiosa y con algunos ajustes puedes potenciar tus resultados!

Para hacer más eficiente tu tiempo y avanzar hacia notas más altas, te sugerimos:
1. Acotar la duración de tus bloques de estudio en la plataforma definiendo un plan de trabajo detallado antes de iniciar sesión.
2. Determinar por escrito el método de resolución más rápido e indicado antes de comenzar a realizar cálculos o responder.
3. Consultar directamente tus dudas con el equipo docente o solicitar una tutoría personalizada para resolver bloqueos puntuales.

¿Qué etapas de la preparación o del desarrollo de la evaluación consideras que demandaron mayor tiempo del esperado?

¡Ánimo, con una mejor selección de estrategias previas lograrás maximizar los frutos de tu esfuerzo en la próxima oportunidad!"""),

    ('evaluations', MID, MID, """El sistema registra que tanto el tiempo dedicado a la evaluación (E1) como tu calificación (E2) se sitúan en la mediana de tu curso (entre el percentil 33 y 66). Mantienes un ritmo regular sobre el cual es posible seguir construyendo.

Para optimizar tus hábitos de estudio e impulsar tu rendimiento hacia un nivel superior, te sugerimos:
1. Elaborar mapas conceptuales, esquemas o resúmenes redactados con tus propias palabras sobre los contenidos centrales.
2. Reflexionar detenidamente sobre los objetivos de cada subsección antes de comenzar a responder las preguntas de la evaluación.
3. Solicitar orientación al equipo docente si tienes dudas o no sabes por dónde empezar a organizar tus repasos.

¿Qué técnicas o herramientas de estudio podrías incorporar para dar un salto cualitativo en tus próximas calificaciones?

¡Comprender tu forma de aprender te dará la claridad para realizar los ajustes necesarios y alcanzar mejores resultados!"""),

    ('evaluations', LOW, MID, """El sistema registra que el tiempo invertido en la evaluación (E1) se encuentra por debajo del percentil 33, mientras que tu calificación (E2) se ubica en la mediana del curso (entre el percentil 33 y 66). Es un buen resultado inicial con un claro margen de mejora.

Para afianzar tus conocimientos y proyectar mejores calificaciones en las siguientes unidades, te sugerimos:
1. Diseñar resúmenes, fichas de estudio (flashcards) o mapas conceptuales con tus propias palabras para consolidar la materia.
2. Formularte preguntas de reflexión previa para comprobar la claridad de tus razonamientos antes de enviar cada respuesta.
3. Planificar el tiempo asignado a cada subsección garantizando que comprendes los objetivos principales de la evaluación.

¿De qué manera dedicar algunos minutos adicionales a la revisión previa te ayudaría a sentir mayor certeza en tus respuestas?

¡Conocer cómo aprendes y ajustar tus estrategias de estudio marcará una gran diferencia en tus futuros logros!"""),

    # ------------------------------------------------------------------
    # Constancia: C1 = unidades completadas por semana, C2 = tiempo conectado por semana
    # ------------------------------------------------------------------
    ('consistency', LOW, LOW, """El sistema registra que tanto las unidades completadas (C1) como tu tiempo de conexión semanal en la plataforma (C2) se encuentran por debajo del percentil 33 de tu curso. Te invitamos a reflexionar sobre tu progreso para identificar si este ritmo responde a falta de tiempo disponible o a dificultades para comprender las actividades propuestas.

Para organizar mejor tu estudio y avanzar con mayor constancia, te sugerimos:
1. Distribuir el tiempo semanal sugerido de trabajo autónomo en pequeños bloques fijos a lo largo de la semana, evitando acumular las tareas antes de las evaluaciones.
2. Definir y registrar en tu calendario personal un bloque horario semanal fijo dedicado exclusivamente al trabajo de esta asignatura.
3. Llevar un registro de todas las actividades que logres completar para visualizar tus progresos y mantener la motivación.

¿De qué manera una distribución más constante del tiempo en tu semana te ayudaría a abordar las tareas con mayor tranquilidad?

¡Paso a paso, organizando tus tiempos y registrando tus avances, recuperarás el impulso para alcanzar tus metas en el curso!"""),

    ('consistency', MID, LOW, """El sistema registra que las unidades completadas (C1) están en la mediana del curso (entre el percentil 33 y 66), mientras que tu tiempo de conexión (C2) se ubica por debajo del percentil 33. Te invitamos a evaluar si esta dinámica se vincula con la gestión del tiempo o con dudas específicas en la comprensión de los contenidos.

Para afianzar lo aprendido y asegurar un avance sólido, te sugerimos:
1. Asignar un bloque horario semanal en tu calendario personal siguiendo las recomendaciones de tiempo de trabajo autónomo del equipo docente.
2. Dedicar unos 15 minutos al final de cada unidad a autoevaluar tu nivel de comprensión respondiendo las preguntas de control de la plataforma.
3. Elaborar un documento de síntesis de una página por cada módulo cerrado para registrar tus avances y cerciorarte de que no queden vacíos conceptuales.

¿Qué estrategia podrías implementar al cerrar cada unidad para comprobar que has asimilado profundamente las ideas centrales?

¡Registrar lo aprendido y evaluar tu progreso de manera continua te dará bases muy firmes para seguir avanzando con éxito!"""),

    ('consistency', MID, HIGH, """El sistema registra que las unidades completadas (C1) se sitúan en la mediana del curso (entre el percentil 33 y 66), mientras que tu tiempo de conexión (C2) supera el percentil 66. Mantienes un avance constante y es un buen momento para buscar mayor eficiencia en tus tiempos de navegación.

Para optimizar tus hábitos de trabajo y afianzar tu rendimiento, te sugerimos:
1. Mantener tu ritmo actual revisando minuciosamente cómo podrías hacer más eficiente tu tiempo dentro de la plataforma.
2. Consultar periódicamente las demás métricas del sistema para reflexionar integralmente sobre tu desempeño académico.
3. Establecer micro-objetivos claros antes de iniciar cada sesión para enfocar tu navegación en tareas específicas.

¿Qué actividades en la plataforma demandan más tiempo y cómo podrías organizar tu trabajo para resolverlas con mayor agilidad?

¡Mantener tu constancia e ir ajustando los tiempos de navegación te permitirá progresar de manera equilibrada y satisfactoria!"""),

    ('consistency', HIGH, HIGH, """El sistema registra que tanto las unidades completadas (C1) como tu tiempo de conexión en la plataforma (C2) se sitúan por sobre el percentil 66 de tu curso. ¡Demuestras una gran dedicación y un compromiso sobresaliente!

Para resguardar la eficiencia de tu estudio y asegurar que tus aprendizajes sean duraderos, te sugerimos:
1. Relacionar los contenidos de las unidades terminadas con escenarios de aplicación real fuera de la plataforma para consolidar lo aprendido.
2. Establecer un límite superior de tiempo de conexión semanal para monitorear tu dedicación, resguardar tu eficiencia y evitar la saturación.
3. Revisar periódicamente las otras métricas de la plataforma para reflexionar sobre tu desempeño global y mantener el equilibrio.

¿De qué forma vincular los contenidos con situaciones o problemas del mundo real te ayuda a darle un sentido práctico a tu estudio?

¡Tu compromiso es admirable; cuidar el balance de tus tiempos te asegurará un rendimiento alto y sostenible a lo largo del curso!"""),

    ('consistency', HIGH, LOW, """El sistema registra que las unidades completadas (C1) superan el percentil 66 de tu curso, mientras que tu tiempo de conexión (C2) se sitúa por debajo del percentil 33. Mantienes un ritmo ágil y es valioso reflexionar sobre tu estrategia para garantizar aprendizajes profundos.

Para verificar que tu rapidez de avance se traduzca en comprensiones sólidas y excelentes resultados evaluativos, te sugerimos:
1. Resolver un ejercicio complejo de desarrollo sin asistencia ni soluciones guiadas de la plataforma antes de dar por cerrado un módulo.
2. Redactar una breve explicación con tus propias palabras justificando el principio conceptual que sustenta el procedimiento empleado.
3. Analizar tus métricas complementarias para evaluar de forma consciente si tu estrategia actual te llevará a los resultados esperados.

¿Sientes que el ritmo con el que cierras las unidades te brinda la preparación suficiente para resolver problemas complejos de forma autónoma?

¡Validar tus conocimientos con ejercicios de desarrollo autónomo te dará total tranquilidad para afrontar los desafíos del curso!"""),

    ('consistency', LOW, HIGH, """El sistema registra que las unidades completadas (C1) se encuentran por debajo del percentil 33, mientras que tu tiempo de conexión semanal (C2) supera el percentil 66 de tu curso. Queremos ayudarte a canalizar esa gran dedicación en avances concretos.

Para transformar tu tiempo en la plataforma en entregas concluidas, te sugerimos:
1. Estructurar tus bloques de trabajo dividiendo el material en micro-objetivos semanales según las pautas docentes.
2. Aplicar la regla de los 15 minutos: si un concepto bloquea tu progreso por más de 15 minutos, detén la tarea y envía tu consulta al foro o grupo de estudio.
3. Revisar tus otras métricas de aprendizaje para evaluar de manera consciente cómo se desarrolla tu ritmo de trabajo.

¿Qué tipo de actividades o dudas específicas suelen ralentizar la finalización de tus unidades cuando estás en la plataforma?

¡Con metas semanales delimitadas y solicitando apoyo oportuno lograrás destrabar tus actividades y avanzar a paso firme!"""),

    ('consistency', HIGH, MID, """El sistema registra que las unidades completadas (C1) superan el percentil 66 de tu curso, mientras que tu tiempo de conexión (C2) se sitúa en la mediana (entre el percentil 33 y 66). Cuentas con un avance rápido que conviene acompañar con espacios de integración conceptual.

Para asegurar que esta estrategia te conduzca a los mejores resultados evaluativos y formativos, te sugerimos:
1. Diseñar un esquema u organizador gráfico propio para integrar de forma transversal los contenidos de las unidades ya completadas.
2. Realizar un ejercicio de reflexión quincenal comparando tus avances actuales con tus metas de desarrollo profesional.
3. Monitorear de forma constante el tiempo que dedicas a la navegación y revisar tus demás métricas en el sistema.

¿De qué manera diseñar organizadores gráficos te ayudaría a conectar las distintas unidades y consolidar lo aprendido?

¡Integrar transversalmente los contenidos y reflexionar sobre tu meta profesional le dará mayor firmeza y propósito a tu rendimiento!"""),

    ('consistency', MID, MID, """El sistema registra que tanto las unidades completadas (C1) como tu tiempo de conexión (C2) se sitúan en la mediana de tu curso (entre el percentil 33 y 66). Tienes un desempeño constante sobre el cual puedes seguir fortaleciendo tus hábitos.

Para afianzar tu planificación y sostener un ritmo constante, te sugerimos:
1. Utilizar semanalmente el tiempo sugerido de trabajo autónomo, distribuyéndolo en pequeños bloques durante la semana en lugar de acumularlo antes de evaluar.
2. Definir un bloque horario semanal fijo para trabajar en el curso y anotarlo expresamente en tu calendario personal.
3. Llevar un registro de todas las actividades que vas completando para monitorear tu progreso y reforzar tu motivación.

¿Qué pequeños ajustes en la organización de tus horarios te permitirían abordar el estudio semanal con mayor comodidad y enfoque?

¡Mantener una planificación estructurada y constantes momentos de revisión te permitirá avanzar con gran seguridad académica!"""),

    # OJO: en la planilla, el texto optimizado de esta fila (C1 bajo, C2 en la
    # mediana) es una copia del de "ambas en la mediana" y no describe este
    # caso. Se carga tal cual; corregirlo desde el admin.
    ('consistency', LOW, MID, """El sistema registra que tanto las unidades completadas (C1) como tu tiempo de conexión (C2) se sitúan en la mediana de tu curso (entre el percentil 33 y 66). Tienes un desempeño constante sobre el cual puedes seguir fortaleciendo tus hábitos.

Para afianzar tu planificación y sostener un ritmo constante, te sugerimos:
1. Utilizar semanalmente el tiempo sugerido de trabajo autónomo, distribuyéndolo en pequeños bloques durante la semana en lugar de acumularlo antes de evaluar.
2. Definir un bloque horario semanal fijo para trabajar en el curso y anotarlo expresamente en tu calendario personal.
3. Llevar un registro de todas las actividades que vas completando para monitorear tu progreso y reforzar tu motivación.

¿Qué pequeños ajustes en la organización de tus horarios te permitirían abordar el estudio semanal con mayor comodidad y enfoque?

¡Mantener una planificación estructurada y constantes momentos de revisión te permitirá avanzar con gran seguridad académica!"""),

    # ------------------------------------------------------------------
    # Videos: V1 = % del video efectivamente visualizado, V2 = interacciones con el video
    # ------------------------------------------------------------------
    ('videos', LOW, LOW, """Hola, {name}.

El sistema registra que tanto la proporción de video visualizada (V1) como tus interacciones con el reproductor (V2) se ubican por debajo del percentil 33 de tu curso. Te invitamos a explorar nuevas formas de aprovechar este recurso audiovisual para respaldar tu estudio.

Para transformar la visualización en una experiencia de aprendizaje más efectiva, te sugerimos:
1. Visualizar los recursos audiovisuales de forma completa y continua para asegurar la adquisición de toda la información evaluable.
2. Adoptar un rol activo haciendo pausas cada 2 o 3 minutos para registrar los conceptos principales en tus apuntes.
3. Solicitar una tutoría con el equipo docente si tienes dudas sobre cómo sintetizar adecuadamente la información de los videos.

¿Qué técnica o hábito sencillo podrías incorporar durante la reproducción para asegurarte de captar las ideas centrales?

¡Asumir un rol activo frente al contenido te dará mayor seguridad y te ayudará a avanzar paso a paso hacia tus objetivos!"""),

    ('videos', MID, LOW, """Hola, {name}.

El sistema registra que la proporción de video visualizada (V1) se encuentra en la mediana del curso (entre el percentil 33 y 66), mientras que tus interacciones con el reproductor (V2) están por debajo del percentil 33.

Para enriquecer tu toma de apuntes y preparar de mejor manera tus evaluaciones, te sugerimos:
1. Hacer pausas obligatorias cada vez que aparezca una definición clave o se desarrollen fórmulas y procedimientos complejos.
2. Tomar apuntes detallados durante las pausas para compararlos con el material oficial del curso y construir un resumen de estudio.
3. Solicitar una tutoría con el cuerpo docente para orientar tu estudio y resolver dudas conceptuales específicas.

¿De qué manera comparar tus apuntes de los videos con las lecturas del curso te ayudaría a aclarar los temas complejos?

¡Estructurar tus resúmenes durante la reproducción te dará bases firmes para afrontar tus exámenes con mayor preparación!"""),

    ('videos', MID, HIGH, """Hola, {name}.

El sistema registra que la proporción de video visualizada (V1) se sitúa en la mediana de tu curso (entre el percentil 33 y 66), mientras que tus interacciones en el reproductor (V2) superan el percentil 66. Esta forma de recorrer el recurso aporta datos valiosos sobre tu aprendizaje.

Para profundizar en la comprensión y hacer tuya la información expuesta, te sugerimos:
1. Pausar el video al revisar un ejercicio para estructurar la secuencia del problema y responder por escrito: "¿por qué se aplica este método aquí?".
2. Poner a prueba el concepto resolviendo un ejercicio práctico de forma manual y pensando en situaciones similares.
3. Reflexionar sobre cómo adaptar o mejorar la estrategia mostrada en pantalla para aplicarla a nuevos problemas.

¿Cómo te ayuda responder por escrito la justificación de cada paso a fijar el procedimiento en tu memoria?

¡Hacer propios los conceptos a través de la práctica te permitirá avanzar con aprendizajes sólidos y duraderos!"""),

    ('videos', HIGH, HIGH, """Hola, {name}.

El sistema registra que tanto la proporción de video visualizada (V1) como tus interacciones con el reproductor (V2) se ubican por sobre el percentil 66 de tu curso. Más allá de la cantidad de acciones, lo valioso es identificar cuáles favorecen tu comprensión.

Para acotar tu esfuerzo y consolidar la información más relevante, te sugerimos:
1. Identificar los fragmentos del video que contienen el núcleo explicativo de mayor complejidad y concentrarte en ellos formulándote preguntas o resolviendo ejercicios.
2. Intentar explicar los conceptos más difíciles con tus propias palabras al finalizar cada segmento clave.
3. Diseñar una ficha técnica de síntesis de una sola página al cerrar el recurso para fijar fórmulas clave, definiciones o conceptos centrales.

¿Qué decisiones o momentos de pausa durante la reproducción sientes que te aportaron mayor claridad al estudiar?

¡Aprender a priorizar los núcleos explicativos te permitirá optimizar tu tiempo de estudio y fijar conocimientos con gran precisión!"""),

    ('videos', HIGH, LOW, """Hola, {name}.

El sistema registra que la proporción de video visualizada (V1) supera el percentil 66 de tu curso, mientras que la cantidad de interacciones (V2) se ubica por debajo del percentil 33. Recorrer el material te da una buena visión general, y el siguiente paso es verificar lo que vas comprendiendo.

Para convertir tu visualización en un proceso de comprobación activa, te sugerimos:
1. Pausar la reproducción al término de cada bloque conceptual e intentar reproducir el ejemplo técnico en tus apuntes sin mirar la pantalla.
2. Explicar a otra persona o en voz alta el procedimiento o la idea central de lo que acabas de revisar.
3. Retroceder al fragmento preciso del video con un propósito de búsqueda específico si se te dificulta reconstruir el paso a paso, acudiendo a tutorías si persisten las dudas.

¿Qué ventajas identificas en intentar reconstruir un procedimiento en tus apuntes antes de continuar viendo el video?

¡Incorporar estos momentos de comprobación te dará la certeza de estar asimilando profundamente cada contenido!"""),

    ('videos', LOW, HIGH, """Hola, {name}.

El sistema registra que la proporción de video visualizada (V1) está por debajo del percentil 33, pero interactuaste varias veces (V2 por sobre el percentil 66) en los fragmentos revisados. Esta es una excelente oportunidad para conectar la información de forma integral.

Para construir una perspectiva completa del tema y medir tu avance, te sugerimos:
1. Visualizar de manera secuencial las secciones del video que omitiste en tu primera revisión para integrar todas las partes del contenido.
2. Redactar un párrafo al cerrar el recurso que conecte las ideas específicas analizadas con el objetivo general del módulo.
3. Evaluar tu nivel de comprensión analizando si la síntesis redactada responde a las metas de la unidad.

¿De qué forma conectar los detalles revisados con el objetivo general de la unidad te ayuda a tener una visión más clara del contenido?

¡Completar la visión de conjunto te permitirá relacionar conceptos con fluidez y construir aprendizajes sólidos!"""),

    ('videos', HIGH, MID, """Hola, {name}.

El sistema registra que la proporción de video visualizada (V1) supera el percentil 66 de tu curso, mientras que tus interacciones en el reproductor (V2) se ubican en la mediana (entre el percentil 33 y 66). Cuentas con un recorrido amplio que sirve como excelente base.

Para profundizar en el monitoreo de tu aprendizaje y conectar la teoría con la práctica, te sugerimos:
1. Registrar por escrito tres aplicaciones prácticas o escenarios reales de tu futura profesión donde el concepto expuesto sea indispensable.
2. Utilizar el recorrido completo del video para estructurar un organizador gráfico o un mapa de decisiones procedimentales propio.
3. Revisar periódicamente este organizador gráfico al resolver las guías de ejercicios de la asignatura.

¿Qué situaciones de tu futura práctica profesional se relacionan directamente con las explicaciones del video?

¡Vincular los conceptos teóricos con escenarios reales le dará un propósito claro y motivador a tu estudio autónomo!"""),

    ('videos', MID, MID, """Hola, {name}.

El sistema registra que tanto la proporción de video visualizada (V1) como tus interacciones con el reproductor (V2) se sitúan en torno a la mediana de tu curso (entre el percentil 33 y 66). Este es un buen momento para darle un propósito más reflexivo a tu estudio.

Para dar un paso adelante en la consolidación de tus conocimientos, te sugerimos:
1. Definir un propósito claro antes de iniciar la reproducción y reflexionar sobre qué afirmaciones puedes contrastar con lecturas o temas anteriores.
2. Comparar los procedimientos expuestos en pantalla con otros ejercicios prácticos resueltos previamente.
3. Compartir y debatir los apuntes y resúmenes extraídos del video con tus compañeros/as de estudio.

¿Qué conceptos del video pudiste relacionar con las lecturas o ejercicios que ya habías trabajado anteriormente?

¡Contrastar la información y compartir tus apuntes con otros te permitirá afianzar tu aprendizaje con mayor profundidad!"""),

    ('videos', LOW, MID, """Hola, {name}.

El sistema registra que la proporción de video visualizada (V1) está por debajo del percentil 33, mientras que tus interacciones (V2) se ubican en la mediana de tu curso (entre el percentil 33 y 66). Lo esencial es asegurar que el recorrido realizado te permita comprender las ideas clave.

Para garantizar una comprensión profunda antes de avanzar a la práctica, te sugerimos:
1. Planificar bloques específicos de visualización completa de los recursos multimedia antes de enfrentarte a la resolución de las guías prácticas.
2. Responder por escrito al finalizar el video la pregunta: "¿para qué sirve este procedimiento y cuándo es el mejor momento para aplicarlo?".
3. Revisar los fragmentos donde se expliquen las respuestas a esa interrogante si notas alguna duda al responder.

¿Cómo te ayuda responder la utilidad práctica de un procedimiento antes de comenzar a resolver la guía de ejercicios?

¡Asegurar la comprensión teórica inicial te dará mucha más agilidad y certeza al momento de resolver tus guías prácticas!"""),
]


def load(apps, schema_editor):
    Case = apps.get_model('eol_learner_profiles', 'RecommendationCase')
    Recommendation = apps.get_model('eol_learner_profiles', 'Recommendation')
    case, _ = Case.objects.get_or_create(key='generic', defaults={'name': 'Genérico'})
    for graph, first_level, second_level, text in INITIAL_TEXTS:
        Recommendation.objects.get_or_create(
            case=case, graph=graph, first_level=first_level, second_level=second_level,
            defaults={'text': text},
        )


def unload(apps, schema_editor):
    Case = apps.get_model('eol_learner_profiles', 'RecommendationCase')
    apps.get_model('eol_learner_profiles', 'Recommendation').objects.filter(case__key='generic').delete()
    Case.objects.filter(key='generic').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('eol_learner_profiles', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load, unload),
    ]
