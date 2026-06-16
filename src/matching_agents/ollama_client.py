from __future__ import annotations

import json
from typing import Any

import requests
from pydantic import BaseModel, ValidationError


class OllamaClient:
    def __init__(
        self,
        model: str = "gemma4:e4b",
        base_url: str = "http://localhost:11434",
        timeout: int = 180,
    ) -> None:
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _extract_json(self, content: str) -> dict[str, Any]:
        text = content.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start >= 0 and end > start:
                return json.loads(text[start : end + 1])
            raise

    def chat_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
        images: list[str] | None = None,
    ) -> BaseModel:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": user_prompt,
                    "images": images or [],
                },
            ],
            "options": {"temperature": 0.1},
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content", "{}")

        raw = self._extract_json(content)
        try:
            return response_model.model_validate(raw)
        except ValidationError as exc:
            raise ValueError(f"Invalid model output: {raw}") from exc
