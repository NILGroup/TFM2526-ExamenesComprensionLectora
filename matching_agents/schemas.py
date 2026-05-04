from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class OrchestratorOutput(BaseModel):
    task_type: Literal["A", "B"]


class MicroResolverOutput(BaseModel):
    reasoning: str = Field(min_length=1)
    question_id: str
    selected_answer_id: str


class MicroReviewerOutput(BaseModel):
    feedback: str = Field(min_length=1)
    status: Literal["pass", "fail"]


class PathBq2aOutput(BaseModel):
    reasoning: str = Field(min_length=1)
    question_id: str
    selected_answer_id: str


class PathBa2qOutput(BaseModel):
    reasoning: str = Field(min_length=1)
    answer_id: str
    question_id: str | None = None


class PathBDuelOutput(BaseModel):
    reasoning: str = Field(min_length=1)
    winning_answer_id: str


class PathBAuditOutput(BaseModel):
    is_valid: bool
    reasoning: str = Field(min_length=1)


class PathBAuditBatchOutput(BaseModel):
    reasoning: str = Field(min_length=1)
    selected_answer_id: str | None = None