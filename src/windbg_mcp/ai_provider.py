"""AI Provider Configuration & Dynamic Resolution Engine for WinDbgMCP.

Provides multi-provider support for Google Gemini, OpenAI, Anthropic, Mistral,
Groq, Cerebras, Ollama, LM Studio, and OpenRouter with strict environment variable resolution.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional


class AIProviderConfig:
    """Configures AI provider API keys, base URLs, and model settings strictly from environment variables."""

    def __init__(
        self,
        provider: str = "openrouter",
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
    ):
        self.provider = provider.lower().strip() if provider else "openrouter"
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

        self._configure()

    def _configure(self) -> None:
        if self.provider == "gemini":
            self.api_key = self.api_key or os.environ.get("GEMINI_API_KEY")
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set.")
            self.base_url = (self.base_url or "https://generativelanguage.googleapis.com").rstrip("/")
            if self.model.startswith("models/"):
                self.model = self.model.replace("models/", "", 1)

        elif self.provider == "mistral":
            self.base_url = (self.base_url or "https://api.mistral.ai/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("MISTRAL_API_KEY")
            if not self.api_key:
                raise ValueError("MISTRAL_API_KEY environment variable is not set.")

        elif self.provider == "groq":
            self.base_url = (self.base_url or "https://api.groq.com/openai/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("GROQ_API_KEY")
            if not self.api_key:
                raise ValueError("GROQ_API_KEY environment variable is not set.")

        elif self.provider == "cerebras":
            self.base_url = (self.base_url or "https://api.cerebras.ai/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("CEREBRAS_API_KEY")
            if not self.api_key:
                raise ValueError("CEREBRAS_API_KEY environment variable is not set.")

        elif self.provider == "openai":
            self.base_url = (self.base_url or "https://api.openai.com/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")

        elif self.provider == "anthropic":
            self.base_url = (self.base_url or "https://api.anthropic.com/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is not set.")

        elif self.provider == "ollama":
            self.base_url = (self.base_url or os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/v1")).rstrip("/")
            self.api_key = self.api_key or os.environ.get("OLLAMA_API_KEY")
            if not self.api_key:
                raise ValueError("OLLAMA_API_KEY environment variable is not set.")

        elif self.provider == "ollama_local":
            self.base_url = (
                self.base_url or os.environ.get("OLLAMA_LOCAL_BASE_URL", "http://localhost:11434/v1")
            ).rstrip("/")
            self.api_key = self.api_key or "ollama"

        elif self.provider in ("local", "lmstudio"):
            self.base_url = (
                self.base_url or os.environ.get("LOCAL_LLM_BASE_URL", "http://localhost:1234/v1")
            ).rstrip("/")
            self.api_key = self.api_key or "lm-studio"

        elif self.provider in ("grok", "xai"):
            self.base_url = (self.base_url or "https://api.x.ai/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("XAI_API_KEY")
            if not self.api_key:
                raise ValueError("XAI_API_KEY environment variable is not set.")

        elif self.provider == "deepseek":
            self.base_url = (self.base_url or "https://api.deepseek.com/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("DEEPSEEK_API_KEY")
            if not self.api_key:
                raise ValueError("DEEPSEEK_API_KEY environment variable is not set.")

        elif self.provider == "together":
            self.base_url = (self.base_url or "https://api.together.xyz/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("TOGETHER_API_KEY")
            if not self.api_key:
                raise ValueError("TOGETHER_API_KEY environment variable is not set.")

        elif self.provider == "fireworks":
            self.base_url = (self.base_url or "https://api.fireworks.ai/inference/v1").rstrip("/")
            self.api_key = self.api_key or os.environ.get("FIREWORKS_API_KEY")
            if not self.api_key:
                raise ValueError("FIREWORKS_API_KEY environment variable is not set.")

        elif self.provider == "perplexity":
            self.base_url = (self.base_url or "https://api.perplexity.ai").rstrip("/")
            self.api_key = self.api_key or os.environ.get("PERPLEXITY_API_KEY")
            if not self.api_key:
                raise ValueError("PERPLEXITY_API_KEY environment variable is not set.")

        elif self.provider == "cohere":
            self.base_url = (self.base_url or "https://api.cohere.com/v2").rstrip("/")
            self.api_key = self.api_key or os.environ.get("COHERE_API_KEY")
            if not self.api_key:
                raise ValueError("COHERE_API_KEY environment variable is not set.")

        else:
            self.provider = "openrouter"
            self.api_key = self.api_key or os.environ.get("OPENROUTER_API_KEY")
            if not self.api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is not set.")
            self.base_url = (self.base_url or "https://openrouter.ai/api/v1").rstrip("/")

    def to_dict(self) -> Dict[str, Any]:
        """Return safe, masked metadata representation of the configured provider."""
        masked_key = (
            f"{self.api_key[:4]}...{self.api_key[-4:]}"
            if self.api_key and len(self.api_key) > 8
            else ("***" if self.api_key else "None")
        )
        return {
            "provider": self.provider,
            "base_url": self.base_url,
            "model": self.model,
            "api_key_set": bool(self.api_key),
            "masked_api_key": masked_key,
        }


RECOMMENDED_MODELS: Dict[str, list[str]] = {
    "gemini": [
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-3.6-flash",
        "gemini-3.7-flash",
        "gemini-3.1-flash-lite",
        "gemini-3.1-pro-preview",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.5-pro",
    ],
    "openai": [
        "gpt-5.6",
        "gpt-5.5",
        "gpt-5",
        "gpt-4.5",
        "gpt-4o",
    ],
    "anthropic": [
        "claude-5-opus",
        "claude-4.5-sonnet",
        "claude-4-opus",
        "claude-3-7-sonnet",
        "claude-3-5-sonnet-20241022",
    ],
    "mistral": [
        "codestral-latest",
        "mistral-large-latest",
        "mistral-small-latest",
    ],
    "groq": [
        "deepseek-r1-distill-llama-70b",
        "kimi-k2-instruct",
        "llama-3.3-70b-versatile",
    ],
    "cerebras": [
        "gpt-oss-120b",
        "llama-3.3-70b",
    ],
    "openrouter": [
        "nvidia/nemotron-3-nano-30b-a3b:free",
        "google/gemma-4-31b-it:free",
        "poolside/laguna-s-2.1:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "openai/gpt-oss-20b:free",
    ],
    "ollama": [
        "qwen3-coder",
        "gpt-oss:120b",
        "deepseek-v3.1",
    ],
    "ollama_local": [
        "qwen3-coder",
        "llama3.2",
    ],
    "local": [
        "qwen2.5-coder-14b-instruct-abliterated@q5_k_m",
        "qwen3-14b-abliterated@q5_k_m",
        "codestral-22b-v0.1-abliterated-v3",
        "deepseek-coder-v2-lite-instruct@q5_k_m",
    ],
    "deepseek": [
        "deepseek-reasoner",
        "deepseek-chat",
    ],
    "together": [
        "deepseek-ai/DeepSeek-R1",
        "Qwen/Qwen2.5-Coder-32B-Instruct",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    ],
    "grok": [
        "grok-2-latest",
        "grok-beta",
    ],
    "fireworks": [
        "accounts/fireworks/models/deepseek-r1",
        "accounts/fireworks/models/qwen2p5-coder-32b-instruct",
    ],
    "perplexity": [
        "sonar-pro",
        "sonar-reasoning-pro",
    ],
    "cohere": [
        "command-r-plus",
        "command-r7b-12-2024",
    ],
}


def get_available_ai_providers() -> Dict[str, Dict[str, Any]]:
    """Scan current environment variables and return active AI provider configurations."""
    env_keys = {
        "gemini": "GEMINI_API_KEY",
        "openai": "OPENAI_API_KEY",
        "anthropic": "ANTHROPIC_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "groq": "GROQ_API_KEY",
        "cerebras": "CEREBRAS_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "together": "TOGETHER_API_KEY",
        "grok": "XAI_API_KEY",
        "fireworks": "FIREWORKS_API_KEY",
        "perplexity": "PERPLEXITY_API_KEY",
        "cohere": "COHERE_API_KEY",
        "openrouter": "OPENROUTER_API_KEY",
        "ollama": "OLLAMA_API_KEY",
        "ollama_local": "OLLAMA_LOCAL_BASE_URL",
        "local": "LOCAL_LLM_BASE_URL",
        "lmstudio": "LOCAL_LLM_BASE_URL",
    }

    result = {}
    for provider, env_var in env_keys.items():
        val = os.environ.get(env_var)
        is_set = bool(val) or provider in ("ollama_local", "local", "lmstudio")
        result[provider] = {
            "env_var": env_var,
            "configured": is_set,
            "status": f"{val[:4]}...{val[-4:]}" if val and len(val) > 8 else ("Set" if is_set else "Not Set"),
            "recommended_models": RECOMMENDED_MODELS.get(provider, []),
        }
    return result

