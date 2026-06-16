from __future__ import annotations

import base64
import io
import json
from pathlib import Path
from typing import Any

from PIL import Image

from .state import Item


MAX_IMAGE_SIZE = 512


def _image_to_base64(image_path: Path) -> str | None:
    if not image_path.exists() or not image_path.is_file():
        return None

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail((MAX_IMAGE_SIZE, MAX_IMAGE_SIZE))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)

    return base64.b64encode(buf.getvalue()).decode("ascii")


def _normalize_items(raw_items: list[dict[str, Any]], base_dir: Path) -> list[Item]:
    normalized: list[Item] = []
    for item in raw_items:
        item_id = str(item.get("optionId", "")).strip()
        text = str(item.get("text", "")).strip()
        img_path_raw = str(item.get("image-path", "")).strip()
        image_b64 = None
        if img_path_raw:
            image_b64 = _image_to_base64((base_dir / img_path_raw).resolve())

        normalized.append({"id": item_id, "text": text, "image_b64": image_b64})

    return normalized


def load_matching_exercise(
    json_path: str | Path,
    exam_index: int = 0,
    exercise_index: int = 0,
) -> tuple[list[Item], list[Item], str, dict[str, str], str]:
    path = Path(json_path).resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))

    exercise_entry = payload["exams"][exam_index]["exercises"][exercise_index]
    exercise = exercise_entry["exercise"]
    instructions = str(exercise_entry.get("instructions", "")).strip()
    exercise_id = str(exercise_entry.get("exerciseID", "")).strip()

    answers = _normalize_items(exercise["set1"], path.parent)
    questions = _normalize_items(exercise["set2"], path.parent)

    gold_matches: dict[str, str] = {}
    for question in exercise["set2"]:
        qid = str(question.get("optionId", "")).strip()
        correct = question.get("set1-correct-match")
        if qid and correct is not None:
            gold_matches[qid] = str(correct).strip()

    return questions, answers, instructions, gold_matches, exercise_id
