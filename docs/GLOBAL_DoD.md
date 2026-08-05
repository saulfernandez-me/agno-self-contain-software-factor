# Global Definition of Done (DoD) & Engineering Standards

Este documento define las reglas de calidad y los criterios de aceptación globales que toda Issue, Pull Request y línea de código en **ASSF** debe cumplir antes de considerarse "Terminada".

## 1. Criterios de Aceptación Globales (DoD)

Para que una Issue pase del estado `Implementing` a `Done` (o se fusione en `main`), debe cumplir **todos** los siguientes requisitos:

- [ ] **Funcionalidad:** El código cumple exactamente con la Especificación Técnica detallada en la Issue.
- [ ] **Tests Aprobados:** Todos los tests unitarios y de integración pasan (`pytest`).
- [ ] **Cobertura de Código (Coverage):** El nuevo código mantiene o incrementa la cobertura de tests (mínimo exigido: 80%).
- [ ] **Tipado Estricto:** Pasa la validación de análisis estático de tipos (`mypy --strict`). No se permiten tipos `Any` injustificados.
- [ ] **Linting y Formateo:** El código está formateado y libre de warnings según los estándares del proyecto (`ruff check` y `ruff format`).
- [ ] **Documentación:** Las nuevas clases y funciones públicas tienen docstrings (estilo Google/PEP 257). Si se altera la arquitectura, los archivos en `docs/` o `README.md` deben ser actualizados.
- [ ] **Contratos Pydantic:** Cualquier intercambio de datos estructural está tipado y validado mediante modelos de `Pydantic`.
- [ ] **Revisión por Pares (HITL):** La Pull Request ha sido revisada y aprobada por el Arquitecto de Plataforma (Saúl).

## 2. Estándares del Repositorio

### Gestión de Entorno y Dependencias
- Utilizaremos **`uv`** como el gestor de paquetes y entornos virtuales único y exclusivo.
- Las dependencias de producción se separan estrictamente de las dependencias de desarrollo (`--dev`).

### Estructura de Código (Python)
- **Directorio de código:** `src/assf_core/` (Librería instalable).
- **Directorio de tests:** `tests/` (Espejando la estructura de `src/`).
- **Directorio de templates:** `templates/` (Archivos que se "estamparán" en los repositorios destino).

### Flujo de Git y Commits
- **Ramas:** Todo desarrollo se hace en ramas aisladas con el formato `feat/issue-<numero>-<descripcion_corta>`, `fix/...` o `chore/...`.
- **Commits:** Se exige el uso estricto de **Conventional Commits** (ej. `feat: implement EnvelopeBase validation`, `fix: correct typo in Gate logic`).
- **PRs:** Todo código llega a `main` única y exclusivamente a través de una Pull Request vinculada a su Issue de GitHub correspondiente.