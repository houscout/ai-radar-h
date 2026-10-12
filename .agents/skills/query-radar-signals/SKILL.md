---
name: query-radar-signals
description: "Consultar señales guardadas de AI Radar y Biomedic Radar por fecha, cantidad y orden, ejecutando el script Python de consulta. Activar ante solicitudes como consultar señales, mostrar las últimas señales, dame N señales del día o ver señales por impacto. Consultar ambos radares por defecto; no usar para buscar noticias nuevas ni generar snapshots."
---

# Consultar señales de los radares

Ejecutar siempre el tool Python incluido, en lugar de reconstruir resultados desde la conversación.

## Parámetros

- Seleccionar ambos radares por defecto; respetar una solicitud explícita de solo IA o solo BIO.
- Usar el último snapshot disponible de cada radar si no se especifica fecha. `--day YYYY-MM-DD` selecciona el día del archivo, no la fecha de publicación de la noticia.
- Usar hasta cinco señales por radar si no se especifica cantidad. N significa N por radar; si se pide un total conjunto, aclarar o indicar expresamente cómo se distribuye.
- Ordenar por fecha descendente por defecto. Usar `--order impact` para mayor impacto primero, `title` para título alfabético y `original` para el orden del archivo. `--direction asc|desc` invierte la dirección.
- Resolver referencias como hoy o ayer a una fecha ISO real en America/Matamoros. No seleccionar otra fecha cuando falta el archivo solicitado.

## Ejecutar

Usar Python 3.10 o posterior; el script solo requiere la biblioteca estándar. Resolver scripts/query-signals.py respecto a esta carpeta de skill. Las carpetas predeterminadas son ~/codex y ~/biomedic-radar; pasar --ai-repo o --biomed-repo cuando las ubicaciones sean distintas.

Ejemplo para esta instalación:

```powershell
python C:\Users\CPW\.codex\skills\query-radar-signals\scripts\query-signals.py --radar both --day latest --count 5 --order date --direction desc
```

Traducir los parámetros pedidos a argumentos separados del proceso; no interpolar texto libre del usuario como código de shell. Ejecutar una sola llamada con --radar both para consultar los dos repositorios.

El script devuelve JSON a stdout y códigos de salida 0 (todos disponibles), 1 (faltantes o archivos inválidos, conservando resultados válidos del otro radar), 2 (argumentos incorrectos). Leer el JSON aunque la salida sea 1; informar el problema y fechas disponibles. Si falla la ejecución local, informar que el tool no pudo ejecutarse; no presentar respuestas reconstruidas como resultados del tool.

## Responder

Devolver el JSON solicitado sin alterar sources, evidence, impact, action, state ni biomedical. Explicar brevemente fecha utilizada, cantidad por radar y faltantes si el usuario pide un resumen. N mayor al archivo devuelve solo lo disponible y shortfall; nunca inventar señales.

La respuesta tiene queryVersion, query, returnedCount y results. Cada resultado conserva las señales originales e incluye requestedDay, snapshotDate, availableDays, availableCount, returnedCount y status. No es un nuevo snapshot bajo el contrato diario.

La consulta es de solo lectura: no buscar noticias, actualizar repositorios, publicar datos ni modificar la automatización semanal. El último archivo local puede ser anterior a GitHub; declarar la fecha exacta consultada.
