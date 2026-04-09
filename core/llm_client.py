import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
import time
import json
from core.config import settings


class LLMClient:
    def __init__(self):
        self.provider = settings.llm_provider
        self.request_count = 0

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if self.provider == "ollama":
            return self._call_ollama(prompt, system_prompt)
        elif self.provider == "cohere":
            return self._call_cohere_with_retry(prompt, system_prompt)
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")

    def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        url = f"{settings.ollama_base_url}/api/generate"
        payload = {
            "model": settings.ollama_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "num_predict": 2048,
                "temperature": 0.1,
                "num_ctx": 4096
            }
        }
        try:
            response = requests.post(url, json=payload, timeout=300)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                "Cannot connect to Ollama. "
                "Make sure Ollama is running: open a terminal and run 'ollama serve'"
            )
        except requests.exceptions.Timeout:
            raise TimeoutError("Ollama took too long to respond.")
        except Exception as e:
            raise RuntimeError(f"Ollama error: {str(e)}")

    def _call_cohere_with_retry(self, prompt: str, system_prompt: str = "", max_retries: int = 3) -> str:
        """Calls Cohere with automatic retry on timeout or 5xx errors."""
        self.request_count += 1
        if self.request_count > 1:
            time.sleep(settings.cohere_request_delay)

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                result = self._call_cohere(prompt, system_prompt)
                return result
            except RuntimeError as e:
                last_error = e
                error_str = str(e)
                # Retry on timeout or server errors
                if "timed out" in error_str.lower() or "502" in error_str or "503" in error_str:
                    print(f"Cohere attempt {attempt} failed, retrying in {attempt * 5}s...")
                    time.sleep(attempt * 5)
                else:
                    raise
        raise last_error

    def _call_cohere(self, prompt: str, system_prompt: str = "") -> str:
        try:
            import cohere
            co = cohere.ClientV2(
                api_key=settings.cohere_api_key,
                timeout=120
            )

            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = co.chat(
                model=settings.cohere_model,
                messages=messages
            )
            return response.message.content[0].text.strip()

        except Exception as e:
            raise RuntimeError(f"Cohere error: {str(e)}")

    def generate_json(self, prompt: str, system_prompt: str = "") -> dict:
        json_system = (
            system_prompt +
            "\nRespond with valid JSON only. No explanation, no markdown, no backticks."
        )

        raw = self.generate(prompt, json_system)
        raw = raw.strip()

        if raw.startswith("```"):
            lines = raw.split("\n")
            raw = "\n".join(lines[1:-1]).strip()

        start = raw.find("{")
        if start > 0:
            raw = raw[start:]

        raw = raw.rstrip()
        if raw.endswith(","):
            raw = raw[:-1]

        open_brackets = raw.count("[") - raw.count("]")
        open_braces = raw.count("{") - raw.count("}")

        raw += "]" * open_brackets
        raw += "}" * open_braces

        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError("LLM returned invalid JSON: " + str(e) + "\nRaw response: " + raw)


# Single shared instance — all agents import this
llm_client = LLMClient()