# 🤖 Matching Agents

Este directorio contiene el código del sistema multiagente diseñado para resolver la tarea de **Matching** (emparejamiento) de la tarea PROFE 2026.

## 🚀 Cómo ejecutar el sistema

### 1. Configuración del entorno

Antes de ejecutar los agentes, debes configurar el fichero `.env` en la raíz del proyecto. Este archivo debe contener las credenciales necesarias, particularmente tu API Key de Gemini o configuraciones para otros LLMs.

Para ello, copia el archivo de ejemplo incluido en el repositorio:

```bash
cp .env.example .env
```

A continuación, edita el archivo .env recién creado y sustituye el valor por tu clave de GEMINI:

```
GEMINI_API_KEY="tu_clave_api_aqui"
```

El resto de valores pueden mantenerse tal y como están por defecto.

### 2. Ejecución

Al gestionar el proyecto con `uv`, puedes utilizar `uv run` para ejecutar el código directamente sin necesidad de activar manualmente el entorno virtual. Puedes ejecutar el sistema de dos maneras:

**Opción A: Ejecutando el script principal de Python**

Ejecuta el script de entrada `run_matching.py` desde la raíz del proyecto indicando el fichero JSON de entrada:

```bash
uv run python -m src.matching_agents.run_matching data/dev_matching/matching.json
```
*(Puedes pasar el flag `--exam-index` para probar con un examen en concreto en lugar de todo el conjunto).*

**Opción B: Usando el script de bash (Flujo completo)**

Si deseas ejecutar el pipeline completo (incluyendo inferencia, cálculo de precisión y formato final) con configuración por defecto, puedes lanzar el script en bash desde la raíz:

```bash
./src/matching_agents/run_all.sh
```
El script leerá automáticamente el archivo `.env` y permitirá parametrizar archivos de entrada y salida mediante variables de entorno (como `INPUT_FILE` o `GEMINI_MODEL`).

---

## 📂 Estructura de ficheros

A continuación, se detalla el contenido de cada archivo en este módulo:

* **`agents.py`**: Contiene la lógica y los prompts de cada nodo/agente del grafo
.
* **`calculate_accuracy.py`**: Script para calcular la precisión (accuracy) a partir de los resultados del sistema respecto al ground truth.
* **`convert_to_submission.py`**: Utilidad para dar un formato estándar a las predicciones y ajustarlas al formato esperado por el sistema de evaluación o subida.
* **`dataset.py`**: Gestión, carga y parseo del dataset original de matching (JSON/Imágenes) a las estructuras de datos que los agentes entienden.
* **`evaluate_matching.py`**: Herramientas extra de evaluación detallada sobre los emparejamientos propuestos.
* **`gemini_client.py`**: Wrapper o cliente específico para realizar las peticiones a la API de **Gemini** proporcionando el prompting multimodal u opciones estructuradas.
* **`graph.py`**: Definición principal de la topología de **LangGraph**. Mapea los nodos a los agentes e incluye la condicionalidad y aristas del flujo de ejecución del sistema multiagente.
* **`ollama_client.py`**: Wrapper o cliente local para usar **Ollama** como alternativa (LLMs open-source en local) al modelo propietario.
* **`run_all.sh`**: Script bash orquestador para facilitar la ejecución masiva. Ejecuta la inferencia del modelo y a continuación extrae o calcula puntuaciones sobre el conjunto de datos de validación (dev) o prueba.
* **`run_matching.py`**: Entry-point (CLI principal) en Python para iniciar la ejecución del sistema pasándole por argumento el conjunto de datos deseado de la tarea de matching.
* **`schemas.py`**: Contiene las definiciones estáticas de los tipos usando Pydantic, garantizando *Structured Outputs* fiables a lo largo del paso de mensajes entre agentes LLM.
* **`state.py`**: Define la clase de estado (State) de LangGraph que utilizan los diferentes agentes para compartir la memoria transversal durante cada sesión o ejecución de examen.
