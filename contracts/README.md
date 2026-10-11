# Contrato de señales diarias

Versión: 1.0.0. Proyecto: AI Radar.

El contrato ejecutable se encuentra en `contracts/daily-signals.schema.json` (JSON Schema 2020-12). Los snapshots se guardan en `data/daily/YYYY-MM-DD.json`; la fecha corresponde a America/Matamoros, no al día de publicación de cada noticia. Cada archivo contiene la selección del día, no una recopilación automática programada.

## Campos

- `schemaVersion`, `project`, `domain`, `snapshotDate`, `timezone`, `savedAt`, `language`: identidad y fecha del archivo.
- `collection`: alcance, consultas utilizadas y limitaciones de la búsqueda.
- `signals[].id`: identificador único dentro del snapshot; citar fecha e ID juntos para referirse a una señal.
- `title`, `topic`, `publishedDate`, `studyPublishedDate`: noticia y fecha del estudio cuando se conoce. Usar null si no está verificada.
- `sources`: editor, URL, tipo de fuente y fecha de consulta.
- `evidence`: tipo, resumen, límites y alcance de la revisión.
- `impact`: alto, medio, bajo o desconocido, con justificación editorial. No representa una escala validada.
- `action`: descripción y estado. Las recomendaciones iniciales son proposed.
- `state`: situación del hecho y detalle; separado del estado de la acción.
- `eventGroupId`: agrupa coberturas relacionadas para evitar duplicar impacto; null si no se identificó un grupo.
- `biomedical`: null en AI Radar.

## Reglas de validación

No añadir campos fuera del esquema. Validar tipos, campos obligatorios, fechas ISO y URLs; los IDs no deben repetirse dentro del snapshot. La unicidad se comprueba además del JSON Schema. Si regulatory.status es verified, se requieren jurisdicción, URL y fecha; mientras no exista comprobación se usa not-verified con esos campos en null. La estructura válida no demuestra veracidad de los hechos.

No sobrescribir snapshots existentes: conservar la versión anterior y registrar una revisión separada o un commit revisable. No incluir credenciales ni datos identificables de pacientes. Actualmente no existe scheduler ni integración automática.
