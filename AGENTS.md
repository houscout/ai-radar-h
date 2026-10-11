# Repository Guidelines

## Proyecto y organización

AI Radar organiza novedades de inteligencia artificial en señales accionables.

Lee README.md e inspecciona los archivos antes de implementar. No presentes funcionalidades previstas como existentes. Para futuras incorporaciones, proponemos src/ para módulos, tests/ para pruebas, fixtures/ para ejemplos, public/ para recursos y scripts/ para automatización. Estas rutas deben confirmarse antes de usarlas.

## Comandos de desarrollo

Ejecuta `git status --short` para revisar cambios y `git log -5 --oneline` para consultar el historial. Antes de ejecutar npm, comprueba package.json y sus scripts. No hay comandos de compilación o ejecución local verificados. Documenta los comandos cuando se incorporen.

## Estilo y nombres

Usa dos espacios de indentación en código nuevo, camelCase para variables y funciones, PascalCase para clases y kebab-case para archivos. Mantén módulos pequeños y separa normalización, deduplicación y ranking de la interfaz. Respeta el estilo existente. No se ha verificado ningún formateador o linter.

## Pruebas

El stack propuesto utiliza node:test para dominio y Playwright para interfaz. Nombra las pruebas de dominio como *.test.js. Cuando existan, ejecútalas con `node --test`. Cubre duplicados, datos incompletos y reglas de ranking con fixtures deterministas. No hay umbral de cobertura establecido.

## Commits y pull requests

Convencion propuesta: prefijos docs:, chore:, feat: y fix:. Comprueba el historial local antes de adoptar otros patrones. Mantén commits enfocados. Describe propósito, cambios, verificaciones y limitaciones en cada pull request. Enlaza issues cuando existan y adjunta capturas para cambios visuales.

## Seguridad y trabajo paralelo

No publiques credenciales. Identifica datos ficticios y conserva fuentes y fechas. Replica instrucciones entre AI Radar y Biomedic Radar adaptando el dominio y verificando cada proyecto por separado.

Evalúa novedad, impacto, evidencia y accionabilidad sin inventar capacidades ni adopción.