# 📓 Notebooks y Experimentación

Este directorio contiene todo el código de experimentación, entrenamiento y evaluación de la mayoría de las soluciones desarrolladas durante el trabajo. Muchas de ellas se han implementado en **Jupyter Notebooks (`.ipynb`)**, ya que permite reproducir los experimentos directamente en un entorno de **Google Colab** sin necesidad de ninguna configuración adicional.

---

## 📂 Estructura del Directorio

El directorio está dividido en tres directorios principales, separando el análisis de los datos de las dos tareas en las que se centra el proyecto:

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

> Los notebooks de los directorios `01_multiple_choice/` y `02_matching` están pensados para ejecutarse en Google Colab.

---

## 🏷️ Convención de Nomenclatura

Para facilitar la lectura del contenido del directorio, los archivos siguen un sistema de nomenclatura basado en prefijos numéricos y fases de desarrollo:

Formato general: `[Número]_[Fase]_[Modelo/Estrategia].ipynb`

### 1. Prefijos Numéricos (Series)
* **Serie `00` (Dataset Analysis):** Notebooks dedicados al análisis inicial de los corpus de datos (IC-UNED-RC-ES, PROFE 2025, etc.).
* **Serie `10` (Exploration & Training):** Aquí se encuentran las pruebas de concepto (baselines), experimentación con técnicas de *prompting* (Zero/Few-Shot, Multimodal) y los procesos de entrenamiento (*Fine-Tuning*) de los modelos.
* **Serie `20` (Evaluation):** Ejecuciones definitivas sobre el conjunto de test oficial. Estos notebooks utilizan los modelos o prompts definidos en la fase anterior para generar las inferencias finales sobre los conjuntos de evaluación y poder enviar los resultados a la tarea PROFE 2026.

### 2. Fases
* `analysis`: Análisis de datos y métricas.
* `exploration`: Pruebas de concepto y refinamiento de prompts.
* `training`: Proceso de ajuste fino (*Fine-Tuning*) de modelos locales/abiertos.
* `evaluation`: Inferencia final sobre el conjunto de test oficial de la tarea PROFE 2026.

