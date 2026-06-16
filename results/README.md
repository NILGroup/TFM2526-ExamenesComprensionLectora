# 📊 Resultados y Predicciones

Este directorio contiene todos los resultados de los experimentos y pruebas realizadas durante el desarrollo del proyecto. Esta diseñado para separar claramente las pruebas de concepto y pruebas iniciales de las predicciones oficiales enviadas a la tarea PROFE 2026. Además, se incluye el registro del impacto ambiental y consumo energético de las soluciones presentadas a la competición.

---

## 📂 Estructura del Directorio

El repositorio se divide en las dos tareas principales (`01_multiple_choice` y `02_matching`) e introduce una sub-jerarquía numérica para clasificar el tipo de resultado:

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

Para tener todos los resultados organizados, cada tarea se divide en tres carpetas con propósitos específicos:

### `01_experiments/` (Entorno de Desarrollo)
Contiene las inferencias generadas durante la fase pruebas y experimentación sobre el conjunto de desarrollo correspondiente. Son archivos de uso interno que respaldan las decisiones metodológicas tomadas en los *notebooks* de la serie `10`, pero **no** forman parte de las soluciones propuestas en la competición oficial.

### `02_predictions/` (Resultados Oficiales)
Almacena las predicciones definitivas sobre los conjuntos de *test*. Los archivos aquí siguen la siguiente convención:
* **`_raw.json`**: Salida cruda de los notebooks que incluye la respuesta del modelo,su razonamiento, el nivel del examen, etc.
* **`_formatted.json`**: El archivo final tras pasar por el script de post-procesamiento que sigue el formato requerido para el envío de las soluciones a la competición.

### `03_emissions/` (Sostenibilidad)
Archivos `.csv` que documentan el consumo de energía y las emisiones estimadas de CO2 (medidas con [CodeCarbon](https://codecarbon.io/)). Cada archivo corresponde directamente a una estrategia documentada en la carpeta `02_predictions/`, permitiendo evaluar no solo el rendimiento, sino también la eficiencia energética y el coste de cada enfoque.