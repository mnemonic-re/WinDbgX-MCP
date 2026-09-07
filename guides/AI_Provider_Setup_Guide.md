# WinDbgMCP - Multi-AI Provider Setup & Environment Guide

This document provides complete instructions for configuring and using external AI/LLM providers (Google Gemini, OpenAI, Anthropic, Mistral, Groq, Cerebras, Ollama, LM Studio, OpenRouter) with **WinDbgMCP**, both inside IDE environments (Google Antigravity, Cursor, VS Code, Claude Desktop) and in standalone command-line / terminal setups.

---

## 1. Supported AI Providers & Resolution Logic

WinDbgMCP supports 11 AI provider configurations. **Zero hardcoding rule**: API keys and base URLs are strictly read at runtime from environment variables.

| Provider Name | Required Environment Variable | Default Base URL | Default Model | Notes / Key Format |
| :--- | :--- | :--- | :--- | :--- |
| **`gemini`** | `GEMINI_API_KEY` | `https://generativelanguage.googleapis.com` | `gemini-1.5-pro` | Google Gemini API (`AIzaSy...`). `models/` prefix auto-trimmed. |
| **`openai`** | `OPENAI_API_KEY` | `https://api.openai.com/v1` | `gpt-4o` | Official OpenAI API (`sk-proj-...`). |
| **`anthropic`** | `ANTHROPIC_API_KEY` | `https://api.anthropic.com/v1` | `claude-3-5-sonnet-20240620` | Anthropic Claude API (`sk-ant-...`). |
| **`mistral`** | `MISTRAL_API_KEY` | `https://api.mistral.ai/v1` | `mistral-large-latest` | Mistral AI API platform. |
| **`groq`** | `GROQ_API_KEY` | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` | Groq LPU high-speed inference (`gsk_...`). |
| **`cerebras`** | `CEREBRAS_API_KEY` | `https://api.cerebras.ai/v1` | `llama-3.3-70b` | Cerebras AI wafer-scale inference engine. |
| **`openrouter`** | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` | `auto` | Unified router supporting 100+ open/closed models. |
| **`ollama`** | `OLLAMA_API_KEY` / `OLLAMA_BASE_URL` | `https://ollama.com/v1` | `llama3.2` | Remote Ollama server instance. |
| **`ollama_local`**| `OLLAMA_LOCAL_BASE_URL` | `http://localhost:11434/v1` | `llama3.2` | Local Ollama instance (Key defaults to `ollama`). |
| **`local`** / **`lmstudio`** | `LOCAL_LLM_BASE_URL` | `http://localhost:1234/v1` | `local-model` | Local LM Studio / vLLM / LocalAI endpoint. |

---

## 2. Setting Environment Variables Outside an IDE

If you run `WinDbgMCP` from a command prompt, terminal, batch script, or standalone Python server outside of an IDE, set your environment variables prior to launching the server:

### A. Windows PowerShell
```powershell
# Set for current PowerShell session
$env:GEMINI_API_KEY="AIzaSyYourActualGoogleGeminiKeyHere"
$env:OPENAI_API_KEY="sk-proj-YourActualOpenAIKeyHere"
$env:ANTHROPIC_API_KEY="sk-ant-YourActualAnthropicKeyHere"
$env:MISTRAL_API_KEY="your_mistral_api_key"
$env:GROQ_API_KEY="gsk_your_groq_api_key"
$env:CEREBRAS_API_KEY="csk-your_cerebras_api_key"
$env:OPENROUTER_API_KEY="sk-or-v1-your_openrouter_key"

# Launch WinDbgMCP server
python -m windbg_mcp
```

### B. Windows Command Prompt (CMD)
```cmd
:: Set for current CMD session
set GEMINI_API_KEY=AIzaSyYourActualGoogleGeminiKeyHere
set OPENAI_API_KEY=sk-proj-YourActualOpenAIKeyHere
set ANTHROPIC_API_KEY=sk-ant-YourActualAnthropicKeyHere
set MISTRAL_API_KEY=your_mistral_api_key
set GROQ_API_KEY=gsk_your_groq_api_key

:: Launch WinDbgMCP server
python -m windbg_mcp
```

### C. Permanent Windows Environment Variables (`setx`)
```cmd
:: Persist variables across future command prompt and system sessions
setx GEMINI_API_KEY "AIzaSyYourActualGoogleGeminiKeyHere"
setx OPENAI_API_KEY "sk-proj-YourActualOpenAIKeyHere"
setx ANTHROPIC_API_KEY "sk-ant-YourActualAnthropicKeyHere"
```

### D. Linux / macOS Terminal (Bash / Zsh)
```bash
# Export variables for current terminal session
export GEMINI_API_KEY="AIzaSyYourActualGoogleGeminiKeyHere"
export OPENAI_API_KEY="sk-proj-YourActualOpenAIKeyHere"
export ANTHROPIC_API_KEY="sk-ant-YourActualAnthropicKeyHere"

# Launch WinDbgMCP server
python3 -m windbg_mcp
```

---

## 3. Configuring Environment Variables in IDEs & MCP Clients

When running `WinDbgMCP` inside an IDE or desktop MCP host (Google Antigravity, Cursor, VS Code, Claude Desktop), supply environment variables inside your MCP configuration JSON:

### A. Google Antigravity / Cursor / VS Code (`mcp.json`)
```json
{
  "mcpServers": {
    "windbg-mcp": {
      "command": "python",
      "args": ["-m", "windbg_mcp"],
      "env": {
        "GEMINI_API_KEY": "AIzaSyYourActualGoogleGeminiKeyHere",
        "OPENAI_API_KEY": "sk-proj-YourActualOpenAIKeyHere",
        "ANTHROPIC_API_KEY": "sk-ant-YourActualAnthropicKeyHere",
        "MISTRAL_API_KEY": "your_mistral_key",
        "GROQ_API_KEY": "gsk_your_groq_key",
        "CEREBRAS_API_KEY": "csk-your_cerebras_key",
        "OPENROUTER_API_KEY": "sk-or-v1-your_openrouter_key",
        "LOCAL_LLM_BASE_URL": "http://localhost:1234/v1"
      }
    }
  }
}
```

### B. Claude Desktop (`claude_desktop_config.json`)
```json
{
  "mcpServers": {
    "windbg-mcp": {
      "command": "python",
      "args": ["-m", "windbg_mcp"],
      "env": {
        "GEMINI_API_KEY": "AIzaSyYourActualGoogleGeminiKeyHere"
      }
    }
  }
}
```

---

## 4. Programmatic Python API Usage

You can also initialize and query AI providers programmatically in Python scripts:

```python
import os
from windbg_mcp.ai_provider import AIProviderConfig, get_available_ai_providers

# 1. Scan available environment configurations
status = get_available_ai_providers()
print(f"Gemini Status: {status['gemini']['status']}")

# 2. Configure provider (will read GEMINI_API_KEY from os.environ)
cfg = AIProviderConfig(provider="gemini", model="gemini-1.5-pro")
print(cfg.to_dict())
# Outputs:
# {
#   'provider': 'gemini',
#   'base_url': 'https://generativelanguage.googleapis.com',
#   'model': 'gemini-1.5-pro',
#   'api_key_set': True,
#   'masked_api_key': 'AIza...1234'
# }
```

---

## 5. MCP Tools for AI Provider Management

WinDbgMCP exposes two dedicated FastMCP tools for AI provider inspection:

1. **`get_ai_provider_status`**: Returns Markdown table detailing all 11 providers, associated environment variables, and active configuration states.
2. **`configure_ai_provider(provider, model, base_url, api_key)`**: Dynamically validates and initializes an AI provider configuration object.
