from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class OrchestratorOutput(BaseModel):
    task_type: Literal["A", "B"]


class MicroResolverOutput(BaseModel):
    reasoning: str = Field(min_length=1, description="Razonamiento para escoger la respuesta correcta entre las opciones disponibles. Analiza cada opción una a una, descartándolas si no encajan con el texto o las imágenes (si las hay) proporcionados, y eligiendo la que mejor se ajuste.")
    question_id: str
    selected_answer_id: str


class MicroReviewerOutput(BaseModel):
    reasoning: str = Field(min_length=1, description="Razonamiento para justificar la decisión de aprobar o reprobar la respuesta. Descarta las opciones una a una, asegurándote de que la respuesta elegida es la que mejor encaja.")
    status: Literal["pass", "fail"]
    feedback: str = Field(min_length=1, description="Retroalimentación para el alumno, explicando por qué la respuesta es incorrecta y, si es posible, diciéndole cuál es la respuesta correcta.")


class PathBq2aOutput(BaseModel):
    reasoning: str = Field(min_length=1, description="Razonamiento para escoger el texto que mejor encaja con la pregunta. Analiza cada opción una a una, descartándolas si no encajan con el texto o las imágenes (si las hay) proporcionados, y eligiendo la que mejor se ajuste.")
    question_id: str
    selected_answer_id: str


class PathBa2qOutput(BaseModel):
    reasoning: str = Field(min_length=1, description="Razonamiento para determinar a qué pregunta pertenece la respuesta dada o si es un distractor. Analiza cada opción una a una, descartándolas si no encajan con el texto o las imágenes (si las hay) proporcionados, y eligiendo la que mejor se ajuste.")
    answer_id: str
    question_id: str | None = None

class PathBAuditBatchOutput(BaseModel):
    reasoning: str = Field(min_length=1, description="Razonamiento para determinar cuál de las respuestas propuestas es la que mejor encaja. Analiza cada opción una a una, descartándolas si no encajan con el texto o las imágenes (si las hay) proporcionados, y eligiendo la que mejor se ajuste.")
    selected_answer_id: str | None = None