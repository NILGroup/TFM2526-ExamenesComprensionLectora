from __future__ import annotations

import json
import os
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

try:
    from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore[import-not-found]
except ImportError as exc:  # pragma: no cover - runtime guard
    ChatGoogleGenerativeAI = None  # type: ignore[assignment]
    _LANGCHAIN_GOOGLE_GENAI_IMPORT_ERROR = exc
from pydantic import BaseModel


class GeminiClient:
    """Structured chat client backed by LangChain + Gemini."""

    def __init__(
        self,
        model: str = "gemini-2.5-flash-lite",
        api_key: str | None = None,
        temperature: float = 0.1,
        max_output_tokens: int = 768,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.api_key = "AIzaSyA1nd0cXJjQmL_uHFXdZdFR021EZOLowGQ"
        if not self.api_key:
            raise ValueError(
                "Falta la API key de Gemini. Pasa api_key o define GEMINI_API_KEY/GOOGLE_API_KEY."
            )

        if ChatGoogleGenerativeAI is None:
            raise ImportError(
                "Falta instalar langchain-google-genai en el entorno del proyecto."
            ) from _LANGCHAIN_GOOGLE_GENAI_IMPORT_ERROR

        self.llm = ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
        )

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

    @staticmethod
    def _content_to_text(content: dict[str, Any]) -> str:
        parts = content.get("parts", [])
        texts: list[str] = []
        for part in parts:
            text = part.get("text")
            if isinstance(text, str):
                texts.append(text)
        return "\n".join(texts).strip()

    @staticmethod
    def _build_user_content(user_prompt: str, images: list[str] | None = None) -> list[Any]:
        content: list[Any] = [{"type": "text", "text": user_prompt}]
        for image_b64 in images or []:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                }
            )
        return content

    def chat_structured(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel],
        images: list[str] | None = None,
    ) -> BaseModel:
        structured_llm = self.llm.with_structured_output(response_model)
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=self._build_user_content(user_prompt, images)),
        ]

        raw_result = structured_llm.invoke(messages)

        if isinstance(raw_result, response_model):
            return raw_result

        if isinstance(raw_result, dict):
            raw = raw_result
        else:
            text = getattr(raw_result, "content", "")
            if isinstance(text, str) and text.strip():
                raw = self._extract_json(text)
            else:
                raise ValueError(f"Gemini devolvió una salida no estructurada: {raw_result}")

        try:
            return response_model.model_validate(raw)
        except Exception as exc:
            raise ValueError(f"Invalid model output: {raw}") from exc
