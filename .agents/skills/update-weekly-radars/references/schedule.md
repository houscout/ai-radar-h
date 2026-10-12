# Ejecución semanal

## Configuración instalada en el equipo de CPW

- Programador: tareas de Windows.
- Nombre: AI-Biomed-Radars-Friday.
- Frecuencia: viernes, 09:00.
- Zona: America/Matamoros; el equipo usa Central Standard Time, con la misma regla de horario estacional.
- Primera ejecución programada: 2026-10-16, 09:00.
- Repositorios: houscout/ai-radar-h y houscout/-biomedic-radar-.
- Estado comprobado: tarea registrada y habilitada. Esta configuración corresponde a este equipo, no instala tareas en otras máquinas.

## Recursos locales

La skill personal se encuentra en C:/Users/CPW/.codex/skills/update-weekly-radars.
El entorno Python y runtime.json están en C:/Users/CPW/.codex/radar-weekly.
La tarea ejecuta scripts/run_weekly.py mediante pythonw.exe, sin abrir ventanas.
El runner consulta ambos radares en copias aisladas bajo radar-weekly/checkouts, y publica únicamente snapshots validados.
Consultar radar-weekly/last-run.json para el resultado y radar-weekly/logs para el resumen y registro de Codex.

La primera ejecución completa queda pendiente hasta el viernes; la comprobación de autenticación/acceso y los tests estructurales ya pasaron. El ordenador debe estar encendido, con Internet y la sesión de CPW abierta. No hace falta mantener la interfaz de Codex abierta: se usa Codex CLI con su autenticación existente. Una tarea omitida puede ejecutarse al estar disponible el equipo; los archivos usarán la fecha real.

## Comprobar y ejecutar

Usar el Python de radar-weekly/venv para ejecutar scripts/run_weekly.py --check: comprobar login y acceso remoto sin hacer investigación.
Ejecutar scripts/run_weekly.py sin argumentos para una actualización real autorizada. No duplicar esta tarea en cada repositorio.
Para validar un JSON, usar scripts/validate_snapshot.py SNAPSHOT SCHEMA --weekly; las dependencias están en scripts/requirements.txt.

Consultar la tarea con schtasks /Query /TN AI-Biomed-Radars-Friday /FO LIST /V.
No marcar una búsqueda como publicada si el runner informa failed o partial. Revisar el log, los commits pendientes y las copias de automatización antes de reintentar; no borrar archivos o locks sin comprobar que la ejecución terminó.
