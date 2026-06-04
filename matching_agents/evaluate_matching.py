"""
validate_matching.py
--------------------
Valida un fichero de predicciones (JSONL) contra el dataset de ejercicios
de matching (JSON): comprueba que se han respondido todos los ejercicios
y que las opciones son válidas.

Uso:
    python validate_matching.py --dataset matching.json --predictions matching_baseline.json
"""

import argparse
import json
import sys


# ---------------------------------------------------------------------------
# Carga de ficheros
# ---------------------------------------------------------------------------

def load_dataset(path: str) -> dict[str, dict]:
    """Carga el dataset y devuelve un dict {exerciseID: exercise}."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    exercise_map = {}
    for exam in data.get("exams", []):
        for ex in exam.get("exercises", []):
            if ex.get("type") == "matching":
                exercise_map[ex["exerciseID"]] = ex
    return exercise_map


def load_predictions(path: str) -> dict[str, dict]:
    """Carga el fichero JSONL de predicciones y devuelve un dict {exerciseID: record}."""
    records = {}
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                records[rec["exerciseID"]] = rec
            except (json.JSONDecodeError, KeyError) as e:
                print(f"  [AVISO] Línea {i} no válida en predicciones: {e}", file=sys.stderr)
    return records


# ---------------------------------------------------------------------------
# Validación
# ---------------------------------------------------------------------------

def validate(exercise_map: dict, predictions: dict) -> list[str]:
    errors = []
    all_ids = set(exercise_map.keys()) | set(predictions.keys())

    for ex_id in sorted(all_ids):
        if ex_id not in predictions:
            errors.append(f"[EJERCICIO NO RESPONDIDO] '{ex_id}' está en el dataset pero no en las predicciones")
            continue

        if ex_id not in exercise_map:
            errors.append(f"[EJERCICIO DESCONOCIDO] '{ex_id}' está en las predicciones pero no en el dataset")
            continue

        ex = exercise_map[ex_id]
        result = predictions[ex_id]

        set1_ids = {str(opt["optionId"]) for opt in ex["exercise"]["set1"]}
        expected_set2_ids = {str(opt["optionId"]) for opt in ex["exercise"]["set2"]}

        if result.get("error_procesamiento_json"):
            errors.append(f"[JSON ERROR] '{ex_id}': error_procesamiento_json=true")

        preds = {str(k): str(v) for k, v in result.get("predicciones", {}).items()}

        missing = expected_set2_ids - set(preds.keys())
        extra = set(preds.keys()) - expected_set2_ids
        if missing:
            errors.append(f"[RESPUESTAS FALTANTES] '{ex_id}': set2 ids sin respuesta: {sorted(missing)}")
        if extra:
            errors.append(f"[RESPUESTAS EXTRA] '{ex_id}': claves inesperadas: {sorted(extra)}")

        for set2_id, pred_val in preds.items():
            if set2_id not in expected_set2_ids:
                continue
            if pred_val not in set1_ids:
                errors.append(
                    f"[VALOR INVÁLIDO] '{ex_id}': set2['{set2_id}'] = '{pred_val}' "
                    f"no es un optionId válido de set1. Válidos: {sorted(set1_ids)}"
                )

    return errors


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Valida predicciones de ejercicios de matching.")
    parser.add_argument("--dataset",     required=True, help="Fichero JSON del dataset")
    parser.add_argument("--predictions", required=True, help="Fichero JSONL de predicciones")
    args = parser.parse_args()

    print(f"Dataset:      {args.dataset}")
    print(f"Predicciones: {args.predictions}")
    print()

    exercise_map = load_dataset(args.dataset)
    predictions  = load_predictions(args.predictions)

    print(f"Ejercicios matching en dataset: {len(exercise_map)}")
    print(f"Ejercicios en predicciones:     {len(predictions)}")
    print()

    errors = validate(exercise_map, predictions)

    print("=== VALIDACIÓN ===")
    if errors:
        for e in errors:
            print(" ", e)
    else:
        print("  ✓ Sin errores: todos los ejercicios respondidos con opciones válidas")

    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
