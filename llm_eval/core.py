from __future__ import annotations

import json
import os
import time
import urllib.request
from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass(frozen=True)
class Case:
    id: str
    prompt: str
    reference: str


CASES = (
    Case("arithmetic", "Reply with only the result: 7 + 5", "12"),
    Case("capital", "Reply with only the city: capital of France", "Paris"),
    Case("boolean", "Reply true or false only: 2 is greater than 9", "false"),
)


class Provider(Protocol):
    name: str

    def complete(self, prompt: str) -> tuple[str, int | None]: ...


class FixtureProvider:
    name = "offline-fixture"

    def complete(self, prompt: str) -> tuple[str, int | None]:
        return next((case.reference, None) for case in CASES if case.prompt == prompt)


class CompatibleProvider:
    def __init__(self):
        base_url = os.getenv("LLM_BASE_URL", "").strip().rstrip("/")
        self.name = os.getenv("LLM_MODEL", "").strip()
        if not base_url or not self.name:
            raise ValueError("Set LLM_BASE_URL and LLM_MODEL")
        if not base_url.startswith(("https://", "http://localhost:", "http://127.0.0.1:")):
            raise ValueError("Use HTTPS or localhost HTTP")
        self.url = base_url + "/chat/completions"
        self.key = os.getenv("LLM_API_KEY", "")

    def complete(self, prompt: str) -> tuple[str, int | None]:
        payload = {"model": self.name, "temperature": 0, "messages": [{"role": "user", "content": prompt}]}
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = "Bearer " + self.key
        request = urllib.request.Request(self.url, json.dumps(payload).encode(), headers, method="POST")
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
        return data["choices"][0]["message"]["content"], data.get("usage", {}).get("total_tokens")


def evaluate(provider: Provider, cases=CASES) -> dict:
    rows = []
    for case in cases:
        start = time.perf_counter()
        answer, tokens, error = "", None, None
        try:
            answer, tokens = provider.complete(case.prompt)
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        latency = time.perf_counter() - start
        rows.append({**asdict(case), "answer": answer, "correct": error is None and answer.strip().casefold() == case.reference.casefold(), "latency_seconds": latency, "tokens": tokens, "error": error})
    valid = [r for r in rows if r["error"] is None]
    return {
        "provider": provider.name,
        "cases": rows,
        "summary": {
            "total": len(rows),
            "successful": len(valid),
            "exact_match": sum(r["correct"] for r in rows) / len(rows) if rows else None,
            "mean_latency_seconds": sum(r["latency_seconds"] for r in valid) / len(valid) if valid else None,
            "reported_tokens": sum(r["tokens"] for r in valid if isinstance(r["tokens"], int)) or None,
        },
    }
