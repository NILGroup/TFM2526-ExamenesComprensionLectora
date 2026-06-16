from __future__ import annotations

from typing import Literal, TypedDict


class Item(TypedDict):
    id: str
    text: str
    image_b64: str | None


class MatchingGraphState(TypedDict):
    task_type: Literal["Type_A", "Type_B"] | None
    exercise_instructions: str
    original_questions: list[Item]
    all_answers: list[Item]
    available_answers: list[Item]
    current_matches: dict[str, str]
    tablero_final: dict[str, str]
    borrador_directo: dict[str, str]
    borrador_inverso: dict[str, str | None]
    preguntas_huerfanas: list[str]
    current_question_index: int
    current_question_attempts: int
    global_iteration_count: int
    flagged_questions: list[str]
    latest_micro_candidate: dict[str, str]
    latest_review_feedback: str
