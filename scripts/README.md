# Consultar señales guardadas

Requiere Python 3.10 o posterior, sin paquetes adicionales. Desde la raíz de cualquiera de los dos repositorios:

```powershell
python scripts/query-signals.py --radar both --day latest --count 5
python scripts/query-signals.py --radar both --day 2026-10-11 --count 3 --order impact
python scripts/query-signals.py --radar ai --day latest --count 2 --order date --direction asc
```

N es la cantidad máxima por radar. El día identifica el snapshot archivado, no la fecha de cada noticia. latest selecciona el último archivo de cada radar, que puede tener fechas distintas. Los snapshots actualmente contienen cinco señales y se generan semanalmente; pedir más devuelve lo disponible y shortfall.

Órdenes: date (fecha de publicación), impact (alto, medio, bajo, desconocido), title y original. La dirección predeterminada es desc para fecha/impacto y asc para título/original. Los empates conservan el orden de archivo.

Las carpetas predeterminadas son ~/codex y ~/biomedic-radar. Usar --ai-repo RUTA y --biomed-repo RUTA para otras instalaciones.

La salida es JSON con metadatos de consulta y un resultado por radar; conserva todos los campos de cada señal. No modifica archivos ni ejecuta búsquedas web. El código de salida es 0 si todos los radares solicitados están disponibles, 1 si hay faltantes o archivos inválidos (los otros resultados se conservan), y 2 si los argumentos son incorrectos. No sustituye un día inexistente por el más cercano.

El lector comprueba versión, dominio, fechas, campos de ordenación e identificadores; no realiza una nueva validación científica o completa del JSON Schema diario.

Pruebas: `python tests/query-signals.test.py`.
