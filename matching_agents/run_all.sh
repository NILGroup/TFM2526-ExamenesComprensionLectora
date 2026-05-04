#!/bin/bash
# Script de ejemplo para procesar todos los ejercicios del matching.json y calcular accuracy

set -e

# Variables de configuración
INPUT_FILE="data/matching.json"
OUTPUT_FILE="results_all.json"
ACCURACY_REPORT="accuracy_report.json"
BACKEND="gemini"
GEMINI_MODEL="gemini-2.5-flash-lite"

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
