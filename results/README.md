# 📊 Resultados y Predicciones

Este directorio almacena todos los artefactos estáticos generados durante la ejecución de los modelos. Está diseñado para separar claramente las pruebas de concepto iniciales de las predicciones oficiales enviadas a evaluación, garantizando la total reproducibilidad y transparencia del Trabajo de Fin de Máster.

Además, se incluye el registro del impacto ambiental y consumo energético de las inferencias oficiales, alineándose con las buenas prácticas de la Inteligencia Artificial sostenible.

---

## 📂 Estructura del Directorio

El repositorio mantiene la división por tareas principales (`01_multiple_choice` y `02_matching`) e introduce una sub-jerarquía numérica para clasificar el tipo de resultado:

```text
results/
├── 01_multiple_choice/             # Resultados de la tarea de Opción Múltiple
│   ├── 01_experiments/             # Salidas exploratorias y de desarrollo
│   │   ├── cot_mistral7b.jsonl
│   │   ├── gemma4_cot.json
│   │   ├── gemma4_zero_shot.json
│   │   ├── gemma4_zero_shot_expl.json
│   │   ├── gemma4_zero_shot_fine_tuning.json
│   │   ├── gemma4_zero_shot_no_cuant.json
│   │   ├── mistral7b_simple_reasoning.json
│   │   ├── qwen35_zero_shot.json
│   │   ├── qwen35_zero_shot_fine_tuning.json
│   │   ├── qwen35_zero_shot_no_cuant.json
│   │   └── zs_mistral.json
│   ├── 02_predictions/             # Inferencias oficiales (Test)
│   │   ├── cot_gemma4_test_formatted.json
│   │   ├── cot_gemma4_test_raw.json
│   │   ├── ensemble_test_formatted.json
│   │   ├── ensemble_test_raw.json
│   │   ├── ft_gemma4_test_formatted.json
│   │   ├── ft_gemma4_test_raw.json
│   │   ├── zs_gemma4_test_formatted.json
│   │   ├── zs_gemma4_test_raw.json
│   │   ├── zs_ministral_test_formatted.json
│   │   ├── zs_ministral_test_raw.json
│   │   ├── zs_qwen35_test_formatted.json
│   │   └── zs_qwen35_test_raw.json
│   └── 03_emissions/               # Huella de carbono de las inferencias
│       ├── cot_gemma4_test_emissions.csv
│       ├── ensemble_test_emissions.csv
│       ├── ft_gemma4_test_emissions.csv
│       ├── zs_gemma4_test_emissions.csv
│       ├── zs_ministral_test_emissions.csv
│       └── zs_qwen35_test_emissions.csv
│
└── 02_matching/                    # Resultados de la tarea de Emparejamiento
    ├── 01_experiments/
    │   ├── accuracy_agents_report.json
    │   ├── matching_agents_dev.json
    │   ├── matching_agents_dev_report.json
    │   ├── matching_gemma4_dev.json
    │   └── matching_qwen35_dev.json
    ├── 02_predictions/
    │   ├── agents_test_formatted.json
    │   ├── zs_gemma4_test_formatted.json
    │   ├── zs_gemma4_test_raw.json
    │   ├── zs_qwen35_test_formatted.json
    │   └── zs_qwen35_test_raw.json
    └── 03_emissions/
        ├── gemma4_matching_dev_emissions.csv
        ├── qwen35_matching_dev_emissions.csv
        ├── zs_gemma4_test_emissions.csv
        └── zs_qwen35_test_emissions.csv
```

---

## 🏷️ Convención de Nomenclatura y Subcarpetas

Para evitar la mezcla de datos y facilitar la auditoría de los resultados, cada tarea se divide en tres carpetas con propósitos específicos:

### `01_experiments/` (Entorno de Desarrollo)
Contiene las inferencias crudas generadas durante la fase de diseño de *prompts*, selección de modelos y calibración. Son archivos de uso interno que respaldan las decisiones metodológicas tomadas en los *notebooks* de la serie `10`, pero **no** forman parte de la evaluación final del sistema.

### `02_predictions/` (Resultados Oficiales)
Almacena las predicciones definitivas sobre los conjuntos de prueba (*test*). Los archivos aquí siguen una estricta convención de sufijos:
* **`_raw.json`**: La respuesta exacta y sin procesar generada por el Modelo de Lenguaje (LLM). Fundamental para analizar alucinaciones o errores de formato.
* **`_formatted.json`**: El archivo final tras pasar por el script de post-procesamiento. Este es el formato estandarizado que se envía para el cálculo de las métricas de rendimiento y la competición oficial.

### `03_emissions/` (Sostenibilidad)
Archivos `.csv` que documentan el consumo de energía y las emisiones estimadas de CO2 (usualmente medidos a través de librerías como CodeCarbon). Cada archivo corresponde directamente a una estrategia documentada en la carpeta `02_predictions/`, permitiendo evaluar no solo el rendimiento (*Accuracy* / *F1-Score*), sino también la eficiencia energética y viabilidad de cada enfoque.