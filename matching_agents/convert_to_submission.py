"""
convert_to_submission.py
------------------------
Convierte un fichero JSONL de predicciones al formato de entrega.

Uso:
    python convert_to_submission.py --input matching_baseline.json --output submission.json
"""

import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="Convierte predicciones JSONL al formato de entrega.")
    parser.add_argument("--input",  required=True, help="Fichero JSONL de predicciones")
    parser.add_argument("--output", required=True, help="Fichero JSON de salida")
    args = parser.parse_args()

    submission = {}

    with open(args.input, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"[AVISO] Línea {i} no válida, se omite: {e}", file=sys.stderr)
                continue

            ex_id = rec.get("exerciseID")
            preds = rec.get("predicciones", {})

            if not ex_id:
                print(f"[AVISO] Línea {i} sin 'exerciseID', se omite.", file=sys.stderr)
                continue

            submission[ex_id] = {str(k): str(v) for k, v in preds.items()}

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(submission, f, ensure_ascii=False, indent=2)

    print(f"✓ {len(submission)} ejercicios escritos en '{args.output}'")


if __name__ == "__main__":
    main()
