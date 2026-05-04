from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Calculate accuracy comparing model predictions with gold labels."
    )
    parser.add_argument("gold_file", type=Path, help="Path to original matching JSON with gold labels")
    parser.add_argument("predictions_file", type=Path, help="Path to predictions JSON file")
    parser.add_argument("--output", type=Path, default=None, help="Output file for detailed report")
    return parser.parse_args()


def extract_gold_labels(gold_data: dict[str, Any]) -> dict[str, dict[str, str]]:
    """
    Extract gold labels from the original matching JSON.
    Returns: { exerciseID: { question_id: answer_id, ... }, ... }
    """
    gold_labels: dict[str, dict[str, str]] = {}
    exams = gold_data.get("exams", [])
    
    for exam in exams:
        exercises = exam.get("exercises", [])
        for exercise in exercises:
            exercise_id = exercise.get("exerciseID", "")
            if not exercise_id:
                continue
            
            exercise_data = exercise.get("exercise", {})
            set2 = exercise_data.get("set2", [])
            
            exercise_labels: dict[str, str] = {}
            for question in set2:
                q_id = str(question.get("optionId", "")).strip()
                correct = str(question.get("set1-correct-match", "")).strip()
                if q_id and correct:
                    exercise_labels[q_id] = correct
            
            gold_labels[exercise_id] = exercise_labels
    
    return gold_labels


def calculate_metrics(
    gold: dict[str, str],
    predictions: dict[str, str],
) -> dict[str, Any]:
    """
    Calculate accuracy, precision, recall, and F1 for a single exercise.
    """
    correct = 0
    total = len(gold)
    
    for q_id, gold_answer in gold.items():
        predicted_answer = predictions.get(q_id, "")
        if predicted_answer == gold_answer:
            correct += 1
    
    accuracy = correct / total if total > 0 else 0.0
    
    return {
        "correct": correct,
        "total": total,
        "accuracy": accuracy,
    }


def main() -> None:
    args = parse_args()
    
    # Read files
    gold_data = json.loads(args.gold_file.read_text(encoding="utf-8"))
    predictions_data = json.loads(args.predictions_file.read_text(encoding="utf-8"))
    
    # Extract gold labels
    gold_labels = extract_gold_labels(gold_data)
    
    # Calculate metrics per exercise
    overall_correct = 0
    overall_total = 0
    results_per_exercise: dict[str, dict[str, Any]] = {}
    
    for exercise_id, gold_answers in gold_labels.items():
        predicted_answers = predictions_data.get(exercise_id, {})
        metrics = calculate_metrics(gold_answers, predicted_answers)
        
        results_per_exercise[exercise_id] = {
            "correct": metrics["correct"],
            "total": metrics["total"],
            "accuracy": round(metrics["accuracy"], 4),
        }
        
        overall_correct += metrics["correct"]
        overall_total += metrics["total"]
        
        print(f"{exercise_id}: {metrics['correct']}/{metrics['total']} correct (Accuracy: {metrics['accuracy']:.2%})")
    
    # Overall metrics
    overall_accuracy = overall_correct / overall_total if overall_total > 0 else 0.0
    
    print(f"\n{'='*60}")
    print(f"OVERALL: {overall_correct}/{overall_total} correct (Accuracy: {overall_accuracy:.2%})")
    print(f"{'='*60}")
    
    # Prepare detailed report
    report = {
        "overall": {
            "correct": overall_correct,
            "total": overall_total,
            "accuracy": round(overall_accuracy, 4),
        },
        "per_exercise": results_per_exercise,
    }
    
    # Write report if output specified
    if args.output is not None:
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"\nDetailed report saved to: {args.output}")


if __name__ == "__main__":
    main()
