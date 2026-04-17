from __future__ import annotations

import json
from typing import Any

from openai import OpenAI
from openai import APIConnectionError, APITimeoutError, APIError

from app.config import get_settings


class AIClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.timeout = settings.openai_timeout_seconds
        self.enabled = bool(settings.openai_api_key)
        self._client = (
            OpenAI(api_key=settings.openai_api_key, timeout=self.timeout)
            if self.enabled
            else None
        )

    def generate_json(self, prompt: str, schema_name: str, schema: dict[str, Any]) -> dict[str, Any] | None:
        if not self.enabled or self._client is None:
            return None

        try:
            response = self._client.responses.create(
                model=self.model,
                input=prompt,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": schema_name,
                        "schema": schema,
                        "strict": True,
                    }
                },
            )
            text = self._extract_text(response)
            return json.loads(text) if text else None
        except (APITimeoutError, APIConnectionError, APIError, ValueError, json.JSONDecodeError):
            return None

    def _extract_text(self, response: Any) -> str:
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str) and output_text.strip():
            return output_text

        raw = response.model_dump() if hasattr(response, "model_dump") else response
        fragments: list[str] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("type") == "output_text" and isinstance(node.get("text"), str):
                    fragments.append(node["text"])
                for value in node.values():
                    walk(value)
            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(raw)
        return "\n".join(fragment for fragment in fragments if fragment.strip())


ai_client = AIClient()
