#!/bin/bash
# Script de ejemplo para procesar todos los ejercicios del matching.json y calcular accuracy

set -e

# Cargar variables de entorno si existe el fichero .env
if [ -f .env ]; then
  # shellcheck disable=SC2046
  export $(grep -v '^#' .env | xargs)
fi

# Variables de configuración
INPUT_FILE=${MATCHING_INPUT_FILE:-"data/dev_matching/matching.json"}
OUTPUT_FILE=${MATCHING_OUTPUT_FILE:-"results/02_matching/02_predictions/agents_test_formatted.json"}
ACCURACY_REPORT=${MATCHING_ACCURACY_REPORT:-"results/02_matching/02_predictions/agents_accuracy_report.json"}
BACKEND=${MATCHING_BACKEND:-"gemini"}
GEMINI_MODEL=${MATCHING_GEMINI_MODEL:-"gemini-2.5-flash-lite"}

# Crear directorio de resultados si no existe
mkdir -p "$(dirname "$OUTPUT_FILE")"

echo "========================================="
echo "Procesando todos los ejercicios..."
echo "========================================="

# Ejecutar el procesamiento de todos los ejercicios
uv run run-matching-agents "$INPUT_FILE" \
  --backend "$BACKEND" \
  --gemini-model "$GEMINI_MODEL" \
  --trace \
  --output "$OUTPUT_FILE"

echo ""
echo "✓ Resultados guardados en: $OUTPUT_FILE"
echo ""

echo "========================================="
echo "Calculando accuracy..."
echo "========================================="

# Calcular accuracy
uv run calculate-accuracy "$INPUT_FILE" "$OUTPUT_FILE" --output "$ACCURACY_REPORT"

echo ""
echo "✓ Reporte détallado guardado en: $ACCURACY_REPORT"
echo ""
echo "¡Proceso completado!"
