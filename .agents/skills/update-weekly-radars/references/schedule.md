# Programación semanal

## Configuración solicitada

- Frecuencia: todos los viernes.
- Hora: 09:00.
- Zona horaria: America/Matamoros (respetar cambios de horario mediante la zona IANA).
- Regla: `RRULE:FREQ=WEEKLY;BYDAY=FR;BYHOUR=9;BYMINUTE=0;BYSECOND=0`.
- Proyectos: houscout/ai-radar-h y houscout/-biomedic-radar-.
- Destino: resumen en la tarea programada, con enlaces a los dos JSON.
- Estado de este archivo: configuración preparada; no registra una tarea activa.

## Prompt durable

Usa $update-weekly-radars. Procesa una sola vez ambos repositorios houscout/ai-radar-h y houscout/-biomedic-radar-. Si la skill no está descubierta, lee .agents/skills/update-weekly-radars/SKILL.md del primer repositorio mediante GitHub conectado y sigue sus instrucciones. Lee las guías y contratos vigentes de ambos proyectos. Busca noticias publicadas en los siete días anteriores a la hora real de ejecución en America/Matamoros. Selecciona cinco señales verificables de IA y cinco de biotecnología/ingeniería biomédica, incluyendo Nobel pertinentes solo cuando haya anuncio o actualización en la ventana. Conserva fuente, evidencia y límites, impacto editorial, acción propuesta y estado. Deduplica y revisa fechas. Valida contra el contrato de cada proyecto; guarda el snapshot con fecha local en data/daily/YYYY-MM-DD.json y publícalo en su repositorio. No sobrescribas archivos ni modifiques AGENTS.md. Si faltan señales o falla un acceso, reporta el faltante o resultado parcial sin inventar. Confirma los archivos mediante lectura posterior y devuelve los enlaces con un resumen en español.

## Activación y comprobación

Crear una sola tarea coordinada en Scheduled de la aplicación compatible, usando la hora y zona anteriores. Conectar búsqueda web y GitHub con acceso a ambos repositorios, incluido el privado. No crear dos tareas que ejecuten ambas el modo completo.

Las skills de repositorio estarán disponibles localmente después de descargar cambios. En una tarea con acceso remoto usar la ruta de SKILL.md mediante el conector; no suponer descubrimiento local en la web. Si se usa ejecución local, comprobar que el ordenador y la aplicación permanezcan activos.

Confirmar nombre, identificador de tarea, estado activo y siguiente ejecución antes de anunciar que quedó programada. Probar el prompt y revisar la primera ejecución. Sin herramienta o interfaz de programación accesible, entregar esta configuración y reportar activación pendiente.

No convertir la regla local a un cron UTC fijo; America/Matamoros puede cambiar de offset. No añadir un workflow que requiera credenciales inexistentes ni suponer que guardar este archivo crea una tarea.
