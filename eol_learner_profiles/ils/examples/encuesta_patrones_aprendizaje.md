# Encuesta de Caracterización y Perfil de Aprendizaje

<!--
Instrumento basado en el Inventario de Patrones de Aprendizaje (Vermunt).
Pegar este contenido en el editor de instrumentos ILS (ils_editor) y activarlo.

Puntuación: escala Likert 1..5, el puntaje de cada escala es la MEDIA de sus
ítems (ver eol_learner_profiles/ils/scales_default.json). Cada fila lleva el tag
[dim:<subescala>, item:<n>]; la Sección 1 usa [tag:<nombre>] y no puntúa.
-->

## Sección 1: Datos Demográficos y Contexto

Indique su género [tag:gender]
( ) Femenino
( ) Masculino
( ) Prefiero no responder
( ) Otro (especifique): [has_other_text:true]

¿En qué semestre de la carrera te encuentras? [tag:semester]
( ) Semestre I
( ) Semestre II
( ) Semestre III
( ) Semestre IV
( ) Semestre V
( ) Semestre VI
( ) Semestre VII
( ) Semestre VIII
( ) Semestre IX

Marque la opción que más se asemeje a su contexto actual [tag:work_context]
( ) Estudio y trabajo medio tiempo
( ) Estudio y trabajo tiempo completo
( ) Estudio y soy cuidador(a)
( ) Estudio
( ) Otro: [has_other_text:true]

Seleccione el medio por el cuál se enteró de esta encuesta [tag:referral]
( ) Me enteré a través del foro del curso
( ) Me enteré a través del centro de estudiantes de mi carrera
( ) Me enteré por un amigo
( ) Otro: [has_other_text:true]

---

## Parte A: Opiniones sobre el estudio

A continuación, para cada enunciado señala hasta qué grado éste se aplica a lo que opinas sobre ti mismo/a.

Leyenda: 1 = Totalmente en desacuerdo | 2 = En desacuerdo en su mayor parte | 3 = Indeciso/a | 4 = De acuerdo en su mayor parte | 5 = Totalmente de acuerdo

### A.1 Concepciones de aprendizaje

| Enunciado | 1 | 2 | 3 | 4 | 5 | Dimensión |
|---|:-:|:-:|:-:|:-:|:-:|---|
| Para mí, aprender significa intentar enfocar un problema desde diversos ángulos, incluyendo aspectos que antes me fueran desconocidos | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:construccion_conocimiento, item:1] |
| Las cosas que aprendo tienen que ser útiles para resolver problemas prácticos | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:uso_conocimiento, item:2] |
| Para mí, aprender es asegurarme de que puedo reproducir los contenidos presentados en un curso o asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:absorcion_conocimiento, item:3] |
| Cuando tengo dificultad para entender algunos temas, prefiero pedir ayuda a otros estudiantes | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:aprendizaje_cooperativo, item:4] |
| Cuando presento dificultades para entender algo, el profesor/a debería animarme a encontrar una solución por mí mismo/a | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:aprendizaje_estimulado, item:5] |
| Por mi propia iniciativa, debería intentar elaborar mis propios ejemplos con los materiales de estudio | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:construccion_conocimiento, item:6] |
| Para mí, aprender significa adquirir conocimientos que puedo usar en situaciones de la vida diaria | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:uso_conocimiento, item:7] |
| Debería memorizar definiciones y otros hechos por mi cuenta | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:absorcion_conocimiento, item:8] |
| Considero importante recibir asesoría de otros/as estudiantes acerca de cómo enfocar mis estudios | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:aprendizaje_cooperativo, item:9] |
| El profesor/a debería animarme a reflexionar sobre mis métodos de estudio y sobre cómo desarrollar una mejor forma de estudiar | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:aprendizaje_estimulado, item:10] |
| Con el fin de aprender, yo tendría que resumir el/los tema/s con mis propias palabras | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:construccion_conocimiento, item:11] |
| Para mí, aprender significa tratar de recordar los contenidos que se imparten en una asignatura o materia | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:absorcion_conocimiento, item:12] |
| El profesor/a debería motivarme y darme ánimos | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:aprendizaje_estimulado, item:13] |
| Cuando me preparo para un examen, prefiero hacerlo en equipo con otros compañeros/as | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:aprendizaje_cooperativo, item:14] |
| Para mí, el aprendizaje significa proveerme de información que puedo utilizar de inmediato, a corto o a largo plazo | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:uso_conocimiento, item:15] |

### A.2 Orientaciones motivacionales

| Enunciado | 1 | 2 | 3 | 4 | 5 | Dimensión |
|---|:-:|:-:|:-:|:-:|:-:|---|
| Hago estos estudios porque me gusta aprender y estudiar | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_personal, item:16] |
| Quiero demostrarles a otros que soy capaz de seguir un programa de estudios universitarios con éxito | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_autoevaluacion, item:17] |
| Lo que deseo adquirir, por sobre todo, con mis estudios es capacidad profesional | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_vocacional, item:18] |
| Tengo poca confianza en mi capacidad para estudiar | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_ambivalente, item:19] |
| Tengo por objetivo alcanzar altos niveles de logros académicos | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_certificado, item:20] |
| Quiero descubrir mis propias cualidades, las cosas que soy capaz e incapaz de hacer | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_autoevaluacion, item:21] |
| Me pregunto, si estos estudios merecen la pena de tanto esfuerzo | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_ambivalente, item:22] |
| Estudio básicamente para aprobar los exámenes | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_certificado, item:23] |
| Dudo sobre si éste tipo de educación es la adecuada para mí | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_ambivalente, item:24] |
| Quiero probarme a mí mismo/a que soy capaz de realizar estudios universitarios | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_autoevaluacion, item:25] |
| Cuando puedo elegir opto por cursos o asignaturas que se adapten a mis intereses personales | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_personal, item:26] |
| Cuando puedo elegir, opto por cursos que parezcan útiles para mi trabajo actual o futura profesión | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_vocacional, item:27] |
| Para mí, la prueba escrita de haber aprobado un examen representa algo valioso en sí mismo | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_certificado, item:28] |
| Realizo estos estudios por el puro interés en los temas que se tratan | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_personal, item:29] |
| El propósito principal de mis estudios es prepararme para una profesión | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:orient_vocacional, item:30] |

---

## Parte B: Actividades de estudio

A continuación se describen actividades que puedes realizar al estudiar. Indica con qué frecuencia las llevas a cabo.

Leyenda: 1 = Nunca o casi nunca | 2 = Rara vez | 3 = A veces | 4 = Con frecuencia | 5 = Siempre o casi siempre

### B.1 Estrategias de procesamiento

| Enunciado | 1 | 2 | 3 | 4 | 5 | Dimensión |
|---|:-:|:-:|:-:|:-:|:-:|---|
| Obtengo mis propias conclusiones basándome en los datos que se presentan en un curso o asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_critico, item:31] |
| Memorizo el significado de cada concepto que me es desconocido | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_memorizar_ensayar, item:32] |
| Estudio, en profundidad, los detalles de un tema | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_analizar, item:33] |
| Uso lo que aprendo en un curso fuera de mis actividades de estudio | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_concreto, item:34] |
| Trato de relacionar el contenido nuevo con el conocimiento previo que ya tengo sobre el tema de la materia o asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_relacionar_estructurar, item:35] |
| Comparo mi punto de vista con el de los autores del texto usado en este curso o asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_critico, item:36] |
| Analizo paso a paso, por separado, los contenidos de una teoría | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_analizar, item:37] |
| Trato de construirme un panorama global de un curso o asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_relacionar_estructurar, item:38] |
| Repito las partes principales del tema o materia, hasta que me las aprendo de memoria | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_memorizar_ensayar, item:39] |
| Intento descubrir las semejanzas y las diferencias entre las teorías que he tratado en un curso o asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_relacionar_estructurar, item:40] |
| Hasta que no domino al detalle un capítulo, no paso al siguiente | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_analizar, item:41] |
| Memorizo definiciones o conceptos tan literalmente como sea posible | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_memorizar_ensayar, item:42] |
| Trato de interpretar eventos de la vida diaria, con la ayuda del conocimiento que he adquirido en un curso o asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_concreto, item:43] |
| Presto especial atención a aquellas partes del curso o asignatura que tienen utilidad práctica | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_concreto, item:44] |
| Procuro ser crítico/a con las interpretaciones de los expertos | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:proc_critico, item:45] |

### B.2 Estrategias de regulación

| Enunciado | 1 | 2 | 3 | 4 | 5 | Dimensión |
|---|:-:|:-:|:-:|:-:|:-:|---|
| Estudio de acuerdo con las instrucciones dadas en los materiales de estudio o según las instrucciones dadas por el profesor/a | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:extreg_procesos, item:46] |
| Además del plan de estudios, consulto otra bibliografía relacionada con los contenidos del curso o asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:autorreg_contenidos, item:47] |
| Cuando empiezo a leer un nuevo capítulo o artículo, primero pienso en la mejor forma de estudiarlo | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:autorreg_procesos_resultados, item:48] |
| Me doy cuenta de que no me queda claro aquello que debo recordar, y aquello que no debo recordar | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:falta_regulacion, item:49] |
| Si no entiendo muy bien un texto trato de encontrar otra bibliografía sobre el tema en cuestión | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:autorreg_contenidos, item:50] |
| Utilizo las instrucciones y los objetivos del curso o asignatura dados por el profesor/a para saber exactamente qué hacer | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:extreg_procesos, item:51] |
| Cuando tengo dificultad para entender alguna parte del tema o materia, trato de analizar por qué es difícil para mí | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:autorreg_procesos_resultados, item:52] |
| Evalúo mis progresos de aprendizaje, únicamente, mediante la realización de cuestionarios, tareas y ejercicios proporcionados por el profesor/a o el libro de texto | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:extreg_resultados, item:53] |
| Me doy cuenta de que las instrucciones de estudio que se dan, no son muy claras para mí | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:falta_regulacion, item:54] |
| Para evaluar el progreso de mi aprendizaje cuando estudio, trato de expresar los aspectos principales con mis propias palabras | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:autorreg_procesos_resultados, item:55] |
| Agrego al tema de estudio información de otras fuentes | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:autorreg_contenidos, item:56] |
| Aprendo todo exactamente como aparece en los libros de texto | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:extreg_procesos, item:57] |
| Considero a la introducción, los objetivos, las instrucciones, las tareas y los exámenes impartidos por el profesor/a, como directrices indispensables para mis estudios | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:extreg_resultados, item:58] |
| Me doy cuenta de que me olvido de pedir ayuda en caso de dificultades | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:falta_regulacion, item:59] |
| Si soy capaz de completar todas las tareas asignadas en los materiales de estudio o por el profesor/a, concluyo que tengo un buen dominio del tema o de la asignatura | ( ) | ( ) | ( ) | ( ) | ( ) | [dim:extreg_resultados, item:60] |
