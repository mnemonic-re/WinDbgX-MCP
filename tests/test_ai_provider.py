"""Unit tests for AIProviderConfig and environment variable resolution engine using standard unittest."""

import os
import unittest
from windbg_mcp.ai_provider import AIProviderConfig, get_available_ai_providers


class TestAIProviderConfig(unittest.TestCase):

    def test_gemini_provider_env(self):
        os.environ["GEMINI_API_KEY"] = "test_gemini_key_12345"
        try:
            cfg = AIProviderConfig(provider="gemini", model="models/gemini-1.5-pro")
            self.assertEqual(cfg.provider, "gemini")
            self.assertEqual(cfg.api_key, "test_gemini_key_12345")
            self.assertEqual(cfg.base_url, "https://generativelanguage.googleapis.com")
            self.assertEqual(cfg.model, "gemini-1.5-pro")
        finally:
            os.environ.pop("GEMINI_API_KEY", None)

    def test_gemini_missing_env(self):
        os.environ.pop("GEMINI_API_KEY", None)
        with self.assertRaises(ValueError):
            AIProviderConfig(provider="gemini")

    def test_mistral_provider_env(self):
        os.environ["MISTRAL_API_KEY"] = "test_mistral_key_67890"
        try:
            cfg = AIProviderConfig(provider="mistral")
            self.assertEqual(cfg.provider, "mistral")
            self.assertEqual(cfg.api_key, "test_mistral_key_67890")
            self.assertEqual(cfg.base_url, "https://api.mistral.ai/v1")
        finally:
            os.environ.pop("MISTRAL_API_KEY", None)

    def test_groq_provider_env(self):
        os.environ["GROQ_API_KEY"] = "test_groq_key"
        try:
            cfg = AIProviderConfig(provider="groq")
            self.assertEqual(cfg.provider, "groq")
            self.assertEqual(cfg.base_url, "https://api.groq.com/openai/v1")
        finally:
            os.environ.pop("GROQ_API_KEY", None)

    def test_cerebras_provider_env(self):
        os.environ["CEREBRAS_API_KEY"] = "test_cerebras_key"
        try:
            cfg = AIProviderConfig(provider="cerebras")
            self.assertEqual(cfg.provider, "cerebras")
            self.assertEqual(cfg.base_url, "https://api.cerebras.ai/v1")
        finally:
            os.environ.pop("CEREBRAS_API_KEY", None)

    def test_openai_provider_env(self):
        os.environ["OPENAI_API_KEY"] = "test_openai_key"
        try:
            cfg = AIProviderConfig(provider="openai")
            self.assertEqual(cfg.provider, "openai")
            self.assertEqual(cfg.base_url, "https://api.openai.com/v1")
        finally:
            os.environ.pop("OPENAI_API_KEY", None)

    def test_anthropic_provider_env(self):
        os.environ["ANTHROPIC_API_KEY"] = "test_anthropic_key"
        try:
            cfg = AIProviderConfig(provider="anthropic")
            self.assertEqual(cfg.provider, "anthropic")
            self.assertEqual(cfg.base_url, "https://api.anthropic.com/v1")
        finally:
            os.environ.pop("ANTHROPIC_API_KEY", None)

    def test_ollama_local_provider(self):
        os.environ.pop("OLLAMA_LOCAL_BASE_URL", None)
        cfg = AIProviderConfig(provider="ollama_local")
        self.assertEqual(cfg.provider, "ollama_local")
        self.assertEqual(cfg.base_url, "http://localhost:11434/v1")
        self.assertEqual(cfg.api_key, "ollama")

    def test_lmstudio_local_provider(self):
        os.environ.pop("LOCAL_LLM_BASE_URL", None)
        cfg = AIProviderConfig(provider="lmstudio")
        self.assertEqual(cfg.provider, "lmstudio")
        self.assertEqual(cfg.base_url, "http://localhost:1234/v1")
        self.assertEqual(cfg.api_key, "lm-studio")

    def test_default_openrouter(self):
        os.environ["OPENROUTER_API_KEY"] = "test_openrouter_key"
        try:
            cfg = AIProviderConfig(provider="unknown_provider")
            self.assertEqual(cfg.provider, "openrouter")
            self.assertEqual(cfg.api_key, "test_openrouter_key")
            self.assertEqual(cfg.base_url, "https://openrouter.ai/api/v1")
        finally:
            os.environ.pop("OPENROUTER_API_KEY", None)

    def test_get_available_ai_providers(self):
        providers = get_available_ai_providers()
        self.assertIn("gemini", providers)
        self.assertIn("openai", providers)
        self.assertIn("ollama_local", providers)
        self.assertTrue(providers["ollama_local"]["configured"])


if __name__ == "__main__":
    unittest.main()
