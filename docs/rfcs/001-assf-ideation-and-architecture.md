# RFC 001: Agno Self-Contain Software Factor (ASSF) - Ideación y Arquitectura Base

**Estado:** Aceptado
**Autor:** Saúl Fernández (Arquitecto de Plataforma) / Tachikoma (Tech Lead)
**Fecha:** Agosto 2026

---

## 1. El Problema (Origen de la Necesidad)
En la ingeniería de plataformas moderna, delegar tareas complejas de desarrollo a agentes de Inteligencia Artificial (LLMs) presenta un desafío crítico: **el no-determinismo y la pérdida de control del ciclo de vida (SDLC).**

1. **La trampa de los SDKs (Ej. Agno):** Frameworks como Agno proporcionan primitivas excelentes (`Agents`, `Workflows`, `Tools`), pero actúan como un lienzo en blanco. No dictan *cómo* los agentes deben interactuar de forma segura. Esto lleva a arquitecturas donde la IA decide qué paso ejecutar a continuación, resultando en bucles infinitos, alucinaciones de herramientas y un consumo de tokens impredecible.
2. **La trampa del Contexto Conversacional:** Pasar historiales de chat gigantes entre agentes para compartir contexto degrada la atención del modelo y dispara los costes. 
3. **El desafío del Despliegue (Portabilidad):** Las soluciones de orquestación complejas suelen vivir aisladas en repositorios separados, dificultando que un ingeniero de producto utilice la IA directamente en su repositorio de trabajo de manera rápida y sin configuraciones globales.

## 2. La Ideación (Síntesis de Soluciones)
Para resolver esto, ideamos **ASSF**. Nace de la necesidad de fusionar nuestra experiencia interna orquestando `pi-subagents` con las directrices dogmáticas descubiertas en el framework **SSSF (Super Simple Software Factory)** de Dan Disler.

Nuestra ideación se basa en tres axiomas:
* **Si el LLM es probabilístico, el arnés debe ser determinista:** La IA propone soluciones, pero el código Python decide si se aprueban y cuál es el siguiente paso.
* **Si la IA es cara, la validación debe ser gratis:** Los tests y linters (Gates) deben ejecutarse en la máquina host a velocidad nativa, no pidiéndole a la IA que lea la consola.
* **Si el framework es útil, debe ser estamparle (Stampable):** La solución debe poder inyectarse (`stamp`) directamente en cualquier repositorio destino, volviéndolo autónomo y ejecutable vía `uv`.

## 3. Propuesta de Arquitectura (Los Pilares)
ASSF se construirá como un **"Híbrido de Librería y Scaffold"** sobre el SDK de Agno, implementando estrictamente:

1. **Soberanía del Código (AssfWorkflow):** Un motor donde las transiciones de estado son código Python puro, no decisiones del LLM.
2. **Carriles de Ejecución (Lanes):** Separación estricta entre `agent` (cognición), `code` (scripts bash locales) y `engineer` (aprobación humana).
3. **Contratos Físicos (Envelopes):** Los agentes se comunican exclusivamente leyendo y escribiendo archivos JSON validados por `Pydantic`, erradicando el historial de chat como método de traspaso de datos.
4. **Gates de Validación Post-Fase:** Aserciones estáticas que verifican el éxito de una fase (existencia de archivos, tests en verde) antes de avanzar.
5. **Bucles de Corrección (In-Session):** Si un Gate falla, el error estructurado se inyecta en la sesión activa de la IA para su corrección, evitando el coste del reinicio en frío (Cold Restart).

## 4. Innovaciones Propias sobre SSSF
Además de aplicar los dogmas de SSSF, ASSF introduce:
* **Ejecución Visual Bidireccional:** Uso de **Mermaid.js** no solo como documentación, sino como código fuente (parser que convierte grafos Mermaid en flujos Python) y como telemetría (trazas generadas en vivo).
* **Control Plane vía GitHub Issues:** Templatización de Issues y etiquetas de estado (`assf:planning`, `assf:implementing`) para que GitHub sea la interfaz de control asíncrono, reemplazando la interacción exclusiva por terminal.
* **Observabilidad Visual (Tachikoma Dash):** Una UI local para auditar financieramente el consumo de tokens y ver la cascada de ejecución en tiempo real.