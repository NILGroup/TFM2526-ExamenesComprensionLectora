# Resolución Automática de Exámenes de Comprensión Lectora en Español mediante LLMs

## 📖 Descripción del Proyecto

**Resolución Automática de Exámenes de Comprensión Lectora en Español mediante LLMs**

Este repositorio contiene el código, los experimentos y los recursos del Trabajo de Fin de Máster. El proyecto se enmarca en la participación en la tarea **PROFE 2026** (IberLEF 2026), cuyo objetivo es evaluar la capacidad de comprensión lectora automática en español utilizando exámenes oficiales del Instituto Cervantes. Todo ello bajo las mismas condiciones que los candidatos humanos y sin utilizar datos de entrenamiento específicos para la tarea.

### 🎯 Objetivos y Enfoque

El trabajo se centra en resolver dos de las subtareas de la competición: **selección múltiple** y **emparejamiento de textos**. Para resolverlas, se han utilizado distintas estrategias y modelos de lenguaje, buscando desarrollar soluciones que alcanzasen un rendimiento competitivo en la tarea de forma eficiente.

Se han explorado metodologías como:

* Estrategias de *Prompting* (*zero-shot*, *few-shot*, *Chain-of-Thought (CoT)*...)
* *Fine-tuning* de distintos tipos de modelos sobre corpus externos
* Sistemas Multi-agente para la resolución colaborativa de los ejercicios

## 📁 Estructura del Repositorio

A continuación se presenta una visión general de la organización del proyecto. Para obtener información más detallada, cada directorio principal cuenta con su propio archivo `README.md`.

```text
TFM2526-ExamenesComprensionLectora/
├── data/                  # Conjuntos de datos utilizados
│   ├── dev_matching/
│   │   ├── matching.json
│   │   └── ...
│   ├── dev_multiple_choice/
│   │   ├── multiple_choice.json
│   │   ├── subset_100.json
│   │   └── ...
│   └── test/
│       ├── fill_the_gap_dataset.json
│       ├── multiple_choice_dataset.json
│       └── ...
├── notebooks/             # Notebooks de prueba y desarrollo de soluciones
│   ├── README.md
│   ├── 00_dataset_analysis/
│   │   ├── 01_IC-UNED-RC-ES_dataset_analysis.ipynb
│   │   └── ...
│   ├── 01_multiple_choice/
│   │   ├── 10_baseline_ReCoRES_2022.ipynb
│   │   ├── 14_training_gemma4_fine_tuning.ipynb
│   │   └── ...
│   └── 02_matching/
│       ├── 10_exploration_zs_gemma4.ipynb
│       └── ...
├── results/               # Predicciones, resultados y métricas de emisiones (CO2)
│   ├── README.md
│   ├── 01_multiple_choice/
│   │   ├── 01_experiments/
│   │   │   ├── gemma4_zero_shot.json
│   │   │   └── ...
│   │   ├── 02_predictions/
│   │   │   └── ...
│   │   └── 03_emissions/
│   │       └── ...
│   └── 02_matching/
│       └── ...
├── src/                   # Código del sistema multi-agente y utilidades
│   ├── __init__.py
│   ├── matching_agents/
│   │   ├── agents.py
│   │   ├── graph.py
│   │   ├── run_matching.py
│   │   └── ...
│   └── utils/
│       ├── check_anwers.py
│       └── ...
├── pyproject.toml         # Configuración del proyecto y gestión de dependencias
└── README.md              # Documentación principal
```

### 📋 Descripción breve

* **`data/`**: Almacena los conjuntos de datos de desarrollo y test utilizados durante el trabajo, divididos por subtarea (selección múltiple y emparejamiento).
* **`notebooks/`**: Notebooks utilizados para realizar el análisis exploratorio de los datos y para la experimentación y pruebas de las soluciones desarrolladas.
* **`results/`**: Contiene las predicciones generadas por las distintas soluciones probadas, así como el consumo energético y la huella de carbono de los experimentos enviados a la competición oficial.
* **`src/`**: Contiene el código fuente del sistema multi-agente construido para resolver la subtarea de *matching* y algún *script* de evaluación y utilidades del proyecto.
* **`pyproject.toml`**: Archivo principal de configuración del proyecto en Python, donde se definen las dependencias y metadatos del paquete.

## ⚙️ Requisitos e Instalación

La gran mayoría de las soluciones y experimentos de este proyecto se han desarrollado en *notebooks* pensados para ejecutarse directamente en **Google Colab**. Sin embargo, hay partes fundamentales del proyecto que pueden ejecutarse en un **entorno local**:
* 📊 **Análisis exploratorio:** Los *notebooks* de exploración de los conjuntos de datos ([`notebooks/00_dataset_analysis`](https://github.com/NILGroup/TFM2526-ExamenesComprensionLectora/tree/main/notebooks/00_dataset_analysis)).
* 🤖 **Sistema Multi-agente:** El código fuente para la resolución colaborativa de la tarea de emparejamiento ([`src/matching_agents`](https://github.com/NILGroup/TFM2526-ExamenesComprensionLectora/tree/main/src/matching_agents)).

### Instalación Local

Para levantar el entorno local, este proyecto utiliza `uv` como gestor de paquetes. Los pasos son muy sencillos:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/NILGroup/TFM2526-ExamenesComprensionLectora.git
   cd TFM2526-ExamenesComprensionLectora
   ```

2. **Sincronizar el entorno:**
   Con un solo comando, `uv` se encargará de crear el entorno virtual y bajar todas las dependencias necesarias:
   ```bash
   uv sync
   ```

### 🤖 Ejecución del Sistema Multi-agente

El sistema multi-agente requiere cierta configuración previa de variables de entorno. Por ello, para poder comprender el funcionamiento del sistema y ejecutarlo, se debe consultar la documentación del directorio correspondiente:

👉 **[Guía de configuración y ejecución del Sistema Multi-agente](https://github.com/NILGroup/TFM2526-ExamenesComprensionLectora/tree/main/src/matching_agents)**

## ✍️ Autores

Este proyecto ha sido desarrollado como TFM del Máster en Inteligencia Artificial de la UCM. 

* **[Pablo Folgueira Galán](https://github.com/pfolgueira)** - Autor
* **[Alberto Díaz Esteban](https://github.com/albertodiazatfdi)** - Tutor del TFM

## 📄 Licencia

El código fuente y software desarrollados para este proyecto está bajo la **Licencia MIT**. Para más detalles, consulta el archivo [LICENSE](LICENSE) incluido en este repositorio.
