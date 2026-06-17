from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from dotenv import load_dotenv

from .graph import MatchingAgentSystem

load_dotenv()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run bifurcated multimodal matching agent framework."
    )
    parser.add_argument("input", type=Path, help="Path to matching JSON input")
    parser.add_argument(
        "--exam-index", type=int, default=None,
        help="Index of specific exam to process (default: all)"
    )
    parser.add_argument(
        "--exercise-index", type=int, default=None,
        help="Index of specific exercise to process (default: all)"
    )
    parser.add_argument(
        "--backend",
        choices=["ollama", "gemini"],
        default="ollama",
        help="Backend de inferencia: ollama (local API) o gemini (API de Google).",
    )
    parser.add_argument("--model", default="gemma4:e4b")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    parser.add_argument(
        "--gemini-model",
        default="gemini-2.5-flash-lite",
        help="Modelo Gemini a usar cuando --backend gemini esté activo.",
    )
    parser.add_argument(
        "--gemini-api-key",
        default=None,
        help="API key de Gemini. Si no se pasa, se leen GEMINI_API_KEY o GOOGLE_API_KEY.",
    )
    parser.add_argument(
        "--gemini-base-url",
        default="https://generativelanguage.googleapis.com/v1beta",
        help="Base URL de la API Gemini.",
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Número de ejercicios a procesar antes de hacer una pausa (default: 1).",
    )
    parser.add_argument(
        "--batch-pause-seconds",
        type=float,
        default=0.0,
        help="Pausa entre lotes para reducir presión sobre la API (default: 0).",
    )
    parser.add_argument(
        "--trace",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Muestra traza detallada del proceso en terminal (default: activado).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    batch_size = max(1, args.batch_size)

    system = MatchingAgentSystem(
        model=args.model,
        ollama_url=args.ollama_url,
        backend=args.backend,
        gemini_model=args.gemini_model,
        gemini_api_key=args.gemini_api_key,
        gemini_base_url=args.gemini_base_url,
        trace=args.trace,
    )
    
    input_data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    exams = input_data.get("exams", [])
    
    exam_indices = [args.exam_index] if args.exam_index is not None else range(len(exams))
    
    combined_results = {}
    jobs: list[tuple[int, int]] = []

    for exam_idx in exam_indices:
        if exam_idx >= len(exams):
            continue

        exam = exams[exam_idx]
        exercises = exam.get("exercises", [])
        exercise_indices = [args.exercise_index] if args.exercise_index is not None else range(len(exercises))

        for exercise_idx in exercise_indices:
            if exercise_idx >= len(exercises):
                continue
            jobs.append((exam_idx, exercise_idx))
    
    for start in range(0, len(jobs), batch_size):
        batch = jobs[start:start + batch_size]
        if args.trace:
            print(
                f"[batch] Procesando lote {start // batch_size + 1} "
                f"({len(batch)} ejercicios, {start + 1}-{start + len(batch)} de {len(jobs)})",
                flush=True,
            )

        for exam_idx, exercise_idx in batch:
            try:
                result = system.solve(
                    args.input,
                    exam_index=exam_idx,
                    exercise_index=exercise_idx,
                )
                combined_results.update(result)
            except Exception as exc:
                if args.trace:
                    print(
                        f"[batch] Error procesando exam={exam_idx} exercise={exercise_idx}: {exc}",
                        flush=True,
                    )
                combined_results[f"exam_{exam_idx}_exercise_{exercise_idx}"] = {
                    "error": str(exc)
                }

        if args.output is not None:
            args.output.write_text(
                json.dumps(combined_results, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

        if args.batch_pause_seconds > 0 and start + batch_size < len(jobs):
            if args.trace:
                print(
                    f"[batch] Pausando {args.batch_pause_seconds:.1f}s antes del siguiente lote.",
                    flush=True,
                )
            time.sleep(args.batch_pause_seconds)

    as_json = json.dumps(combined_results, ensure_ascii=False, indent=2)
    if args.output is None:
        print(as_json)
    else:
        args.output.write_text(as_json, encoding="utf-8")


if __name__ == "__main__":
    main()
