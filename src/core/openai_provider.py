import os
import time
from typing import Dict, Any, Optional, Generator
from openai import OpenAI
from src.core.llm_provider import LLMProvider

DEFAULT_MODEL = "openai/gpt-4o-mini"


def resolve_model_name(model_name: Optional[str] = None) -> str:
    return model_name or os.getenv("MODEL") or os.getenv("DEFAULT_MODEL") or DEFAULT_MODEL


def resolve_base_url(base_url: Optional[str] = None) -> Optional[str]:
    return (
        base_url
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("LLM_ENDPOINT")
        or None
    )


def resolve_api_key(api_key: Optional[str] = None) -> str:
    return (
        api_key
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("OPENROUTER_API_KEY")
        or os.getenv("API_KEY")
        or "no-key"
    )


class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None, base_url: Optional[str] = None):
        resolved_model = resolve_model_name(model_name)
        super().__init__(resolved_model, api_key)
        resolved_base_url = resolve_base_url(base_url)
        resolved_api_key = resolve_api_key(self.api_key)

        client_kwargs: Dict[str, Any] = {
            "api_key": resolved_api_key,
            "base_url": resolved_base_url,
        }
        referer = os.getenv("OPENROUTER_HTTP_REFERER")
        app_name = os.getenv("OPENROUTER_APP_NAME")
        if referer or app_name:
            client_kwargs["default_headers"] = {}
            if referer:
                client_kwargs["default_headers"]["HTTP-Referer"] = referer
            if app_name:
                client_kwargs["default_headers"]["X-Title"] = app_name

        self.client = OpenAI(**client_kwargs)

    @classmethod
    def from_env(cls, model_name: Optional[str] = None, **kwargs: Any) -> "OpenAIProvider":
        return cls(model_name=model_name, **kwargs)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
        )

        end_time = time.time()
        latency_ms = int((end_time - start_time) * 1000)

        # Extraction from OpenAI response
        content = response.choices[0].message.content
        usage = {
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens
        }

        return {
            "content": content,
            "usage": usage,
            "latency_ms": latency_ms,
            "provider": "openai"
        }

    def stream(self, prompt: str, system_prompt: Optional[str] = None) -> Generator[str, None, None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


if __name__ == "__main__":
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from dotenv import load_dotenv
    load_dotenv()

    model = resolve_model_name()
    print(f"Endpoint : {resolve_base_url()}")
    print(f"Model    : {model}")

    provider = OpenAIProvider.from_env()

    prompt = "Say hello in one sentence."
    print(f"User: {prompt}")
    print("Assistant: ", end="", flush=True)

    for chunk in provider.stream(prompt):
        print(chunk, end="", flush=True)
    print()