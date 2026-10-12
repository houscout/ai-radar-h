---
name: update-weekly-radars
description: "Buscar noticias semanales de IA y biotecnología, convertirlas en señales verificables y guardar JSON en AI Radar y Biomedic Radar. Usar para actualizar ambos radares los viernes, generar el resumen semanal o ejecutar manualmente el mismo flujo; no confundir la skill con una tarea programada activa."
---

# Actualizar radares semanales

## Alcance y entradas

Procesar por defecto ambos proyectos de houscout:
- AI Radar: `houscout/ai-radar-h`; carpeta local `C:/Users/CPW/codex`.
- Biomedic Radar (alias AI Biomed / Biomedicine Radar): `houscout/-biomedic-radar-`; carpeta local `C:/Users/CPW/biomedic-radar`.

Aceptar un proyecto explícito para ejecución individual. Para una tarea multiproyecto, ejecutar una sola búsqueda coordinada y evitar que cada instancia repita ambos proyectos.

Usar la hora real de ejecución en America/Matamoros. Buscar anuncios publicados en el intervalo de los siete días anteriores hasta la hora actual; no reutilizar fechas de ejemplos. El viernes a las 09:00 es el horario deseado. Leer [schedule.md](references/schedule.md) al configurar o revisar la programación.

## 1. Inspeccionar

Leer AGENTS.md, README.md, contracts/README.md y contracts/daily-signals.schema.json de cada proyecto; listar snapshots recientes. No modificar AGENTS.md ni el contrato existente para acomodar datos incorrectos. Usar GitHub conectado si el acceso local está bloqueado y registrar la vía utilizada.

Si falta el contrato, crear uno versionado antes de guardar señales, manteniendo separados anuncio, evidencia, juicio editorial y estado. Si no se puede leer un contrato existente, reportar el bloqueo de ese proyecto y continuar el otro sin inventarlo.

## 2. Buscar y seleccionar

Buscar IA: modelos, agentes, seguridad, herramientas, repositorios e investigación. Buscar BIO: ingeniería biomédica, dispositivos, biomateriales, imagen, biosensores, edición genética y biotecnología.

Priorizar fuentes originales: estudios, repositorios, instituciones, fabricantes y registros regulatorios o de ensayos. Consultar el anuncio oficial de Nobel cuando un premio pertinente se anuncie en la semana. No rellenar semanas sin novedades Nobel con anuncios históricos presentados como recientes.

Seleccionar hasta cinco señales distintas por proyecto, priorizando fecha de anuncio verificable y utilidad. Si hay menos de cinco verificables, guardar las disponibles y explicar el faltante; no inventar ni ampliar silenciosamente la ventana.

Abrir cada fuente y comprobar editor, URL, fecha y alcance de sus afirmaciones. Un resultado de buscador no basta para confirmar un hecho. Si una página falla, buscar una alternativa identificada; registrar incertidumbre y no afirmar revisión completa.

## 3. Deduplicar y evaluar

Comparar URL, título, institución, estudio y acontecimiento con la selección y snapshots anteriores. Conservar una señal principal por acontecimiento; enlazar coberturas relacionadas mediante eventGroupId. Repetir un hecho antiguo únicamente si hay una actualización sustancial publicada en la ventana, explicando qué cambió.

Distinguir:
- Fuente primaria institucional de cobertura secundaria; un comunicado de fabricante no es validación independiente.
- Fecha de noticia de fecha del estudio o hecho original.
- Evidencia documentada de hipótesis, métricas comerciales y promesas.
- Impacto editorial alto, medio, bajo o desconocido, con justificación.
- Acción propuesta de tarea ejecutada; usar action.status = proposed inicialmente.

Para BIO, distinguir investigación en bacterias, células, animales y humanos. No inferir eficacia clínica ni aprobación por una noticia, un Nobel o el comienzo de un ensayo. Mantener regulatory.status = not-verified y campos asociados en null hasta comprobar autoridad, jurisdicción y fecha. Excluir datos identificables de pacientes y recomendaciones clínicas individuales.

## 4. Construir y validar JSON

Mantener el contrato vigente. Actualmente se usa v1.0.0 y la carpeta data/daily: el archivo del viernes es un snapshot de la búsqueda semanal, no una captura por cada día.

Completar todas las propiedades exigidas: schemaVersion, project, domain, snapshotDate, timezone, savedAt, language, collection y signals. En collection.scope declarar la ventana exacta y que es selección semanal; conservar consultas reales y limitaciones. El contrato actual exige collection.mode = manual-assisted; no cambiar ese literal sin migración versionada, aunque la ejecución haya sido iniciada por un scheduler.

Para cada señal completar identificador, título, tema, fechas, sources, evidence, impact, action, state, eventGroupId y biomedical. Usar AI-01... o BIO-01...; la identidad archivada es fecha más ID. Usar null para datos opcionales desconocidos, no valores inventados. Mantener biomedical = null para IA.

Validar con JSON Schema 2020-12 y formatos; comprobar además IDs únicos, ventana temporal, URLs verificadas, ausencia de duplicados, coherencia de dominios y evidencia regulatoria si se declara verified. Si no existe validador ejecutable, realizar revisión estructural explícita e informar que no se ejecutó un validador completo. Nunca confundir JSON válido con veracidad científica.

## 5. Guardar y comprobar

Guardar en cada repositorio `data/daily/YYYY-MM-DD.json`, con la fecha local de ejecución. No sobrescribir snapshots existentes: si el día ya está guardado, reportar la ejecución como omitida y enlazar el archivo. Una corrección requiere revisión separada autorizada.

Preparar los dos JSON antes de publicar. Crear archivos mediante GitHub conectado o escribir y publicar mediante Git según herramientas disponibles y autorización de la sesión. Si falla uno, informar resultado parcial; no declarar éxito doble.

Leer de nuevo cada archivo publicado y comparar contenido. Reportar enlaces, conteo, validación realizada, limitaciones y estado por proyecto. No enviar correos ni mensajes externos.

## Salida

Devolver un resumen en español con cinco columnas: Fuente, Evidencia, Impacto, Acción y Estado, separado por radar. Enlazar JSON y señalar faltantes. No ejecutar las acciones recomendadas como parte de esta búsqueda.

La skill define el trabajo; solo un scheduler confirmado puede activarlo semanalmente. No anunciar programación activa sin identificador y confirmación de la herramienta o interfaz.
