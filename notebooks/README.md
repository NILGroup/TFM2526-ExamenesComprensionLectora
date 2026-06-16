# 📓 Notebooks y Experimentación

Este directorio contiene todo el código de experimentación, entrenamiento y evaluación del Trabajo de Fin de Máster. 

La mayoría de las soluciones, pipelines de datos y pruebas de concepto se han desarrollado e implementado en **Jupyter Notebooks (`.ipynb`)**. Esta decisión de diseño permite que el código sea altamente interactivo, visual y, lo más importante, **fácilmente reproducible en Google Colab** sin necesidad de complejas configuraciones de entorno local.

---

## 📂 Estructura del Directorio

El repositorio está dividido en tres áreas lógicas principales, separando el análisis previo de las dos tareas centrales del proyecto:

```text
notebooks/
├── 00_dataset_analysis/            # Análisis exploratorio de los datos (EDA)
│   ├── 01_IC-UNED-RC-ES_dataset_analysis.ipynb
│   ├── 02_PROFE_2025_multiple_choice_dev_analysis.ipynb
│   ├── 03_PROFE_2025_multiple_choice_test_analysis.ipynb
│   └── 04_matching_dev_dataset_analysis.ipynb
│
├── 01_multiple_choice/             # Experimentos para la tarea de Opción Múltiple
│   ├── 10_baseline_ReCoRES_2022.ipynb
│   ├── 11_exploration_prompting.ipynb
│   ├── 12_exploration_multimodal_prompting.ipynb
│   ├── 13_exploration_gemma4_few_shot.ipynb
│   ├── 14_training_gemma4_fine_tuning.ipynb
│   ├── 15_training_qwen35_fine_tuning.ipynb
│   ├── 20_evaluation_zs_gemma4.ipynb
│   ├── 21_evaluation_zs_ministral.ipynb
│   ├── 22_evaluation_zs_qwen35.ipynb
│   ├── 23_evaluation_cot_gemma4.ipynb
│   ├── 24_evaluation_ensemble.ipynb
│   ├── 25_training_ft_gemma4.ipynb
│   └── 26_evaluation_ft_gemma4.ipynb
│
└── 02_matching/                    # Experimentos para la tarea de Emparejamiento
    ├── 10_exploration_zs_gemma4.ipynb
    ├── 11_exploration_zs_qwen35.ipynb
    ├── 20_evaluation_zs_gemma4.ipynb
    └── 21_evaluation_zs_qwen35.ipynb
```

---

## 🏷️ Convención de Nomenclatura

Para facilitar la lectura y la evaluación cronológica del proyecto, todos los archivos siguen un sistema estricto de nomenclatura basado en prefijos numéricos y fases de desarrollo:

Formato general: `[Número]_[Fase]_[Modelo/Estrategia].ipynb`

### 1. Prefijos Numéricos (Series)
* **Serie `00` (Dataset Analysis):** Notebooks dedicados exclusivamente a la carga, limpieza, análisis estadístico y comprensión inicial de los corpus de datos (UNED, PROFE 2025, etc.).
* **Serie `10` (Exploration & Training):** El "entorno de pruebas". Aquí se encuentran las pruebas de concepto (baselines), experimentación con técnicas de *prompting* (Zero/Few-Shot, Multimodal) y los procesos de entrenamiento (*Fine-Tuning*).
* **Serie `20` (Evaluation):** Ejecuciones formales y definitivas. Estos notebooks utilizan los modelos o prompts definidos en la fase anterior para generar las inferencias finales sobre los conjuntos de evaluación y calcular las métricas de rendimiento.

### 2. Fases
* `analysis`: Análisis de datos y métricas.
* `exploration`: Pruebas de concepto y refinamiento de prompts.
* `training`: Proceso de ajuste fino (*Fine-Tuning*) de modelos locales/abiertos.
* `evaluation`: Inferencia final sobre el conjunto de test.

---

## 🚀 Guía de Ejecución en Google Colab

1. **Entorno de GPU:** Para los notebooks de la fase `training` y aquellos que cargan modelos en local (Gemma 4, Qwen 3.5), asegúrate de habilitar un entorno de ejecución con aceleración por hardware (T4 GPU o superior) en Google Colab.
2. **Límites de API:** Al ejecutar los notebooks de la fase `evaluation` que realizan peticiones a APIs externas para tareas como *Zero-Shot* o *Chain-of-Thought*, ten en cuenta que el código está estructurado para procesar las peticiones en lotes. Esto garantiza que la ejecución respete el límite de **15 peticiones por minuto** de las cuentas gratuitas, evitando interrupciones por cuota excedida durante la inferencia de grandes conjuntos de datos.
3. **Rutas de Datos:** Todos los notebooks están configurados para leer los conjuntos de datos asumiendo que la carpeta `data/` se encuentra en el directorio padre o subida directamente al entorno temporal de Colab.