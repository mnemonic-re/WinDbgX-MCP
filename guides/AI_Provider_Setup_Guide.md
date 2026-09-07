# WinDbgMCP - Multi-AI Provider Setup & Environment Guide

This document provides complete instructions for configuring and using external AI/LLM providers (Google Gemini, OpenAI / Codex, Anthropic, Mistral, Groq, Cerebras, Ollama, LM Studio, OpenRouter) with **WinDbgMCP**, both inside IDE environments (Google Antigravity, Cursor, Codex, VS Code, Claude Desktop) and in standalone command-line / terminal setups.

---

## 1. Supported AI Providers & Resolution Logic

WinDbgMCP supports 17 AI provider configurations. **Zero hardcoding rule**: API keys and base URLs are strictly read at runtime from environment variables.

| Provider Name | Required Environment Variable | Default Base URL | Default Model | Notes / Key Format |
| :--- | :--- | :--- | :--- | :--- |
| **`gemini`** | `GEMINI_API_KEY` | `https://generativelanguage.googleapis.com` | `gemini-3.5-flash` | Google Gemini API (`AIzaSy...`). `models/` prefix auto-trimmed. |
| **`openai`** | `OPENAI_API_KEY` | `https://api.openai.com/v1` | `gpt-5.6` | Official OpenAI API (`sk-proj-...`). |
| **`anthropic`** | `ANTHROPIC_API_KEY` | `https://api.anthropic.com/v1` | `claude-5-opus` | Anthropic Claude API (`sk-ant-...`). |
| **`deepseek`** | `DEEPSEEK_API_KEY` | `https://api.deepseek.com/v1` | `deepseek-reasoner` | Official DeepSeek API (V3 & R1 reasoning). |
| **`mistral`** | `MISTRAL_API_KEY` | `https://api.mistral.ai/v1` | `codestral-latest` | Mistral AI API platform. |
| **`groq`** | `GROQ_API_KEY` | `https://api.groq.com/openai/v1` | `deepseek-r1-distill-llama-70b` | Groq LPU high-speed inference (`gsk_...`). |
| **`cerebras`** | `CEREBRAS_API_KEY` | `https://api.cerebras.ai/v1` | `gpt-oss-120b` | Cerebras AI wafer-scale inference engine. |
| **`together`** | `TOGETHER_API_KEY` | `https://api.together.xyz/v1` | `deepseek-ai/DeepSeek-R1` | Together AI open-model inference platform. |
| **`grok`** / **`xai`** | `XAI_API_KEY` | `https://api.x.ai/v1` | `grok-2-latest` | xAI / Grok API endpoint. |
| **`fireworks`** | `FIREWORKS_API_KEY` | `https://api.fireworks.ai/inference/v1` | `accounts/fireworks/models/deepseek-r1` | Fireworks fast inference engine. |
| **`perplexity`** | `PERPLEXITY_API_KEY` | `https://api.perplexity.ai` | `sonar-pro` | Perplexity search-augmented LLM API. |
| **`cohere`** | `COHERE_API_KEY` | `https://api.cohere.com/v2` | `command-r-plus` | Cohere Enterprise AI platform. |
| **`openrouter`** | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` | `nvidia/nemotron-3-nano-30b-a3b:free` | Unified router supporting free & paid models. |
| **`ollama`** | `OLLAMA_API_KEY` / `OLLAMA_BASE_URL` | `https://ollama.com/v1` | `qwen3-coder` | Remote Ollama server instance. |
| **`ollama_local`**| `OLLAMA_LOCAL_BASE_URL` | `http://localhost:11434/v1` | `qwen3-coder` | Local Ollama instance (Key defaults to `ollama`). |
| **`local`** / **`lmstudio`** | `LOCAL_LLM_BASE_URL` | `http://localhost:1234/v1` | `qwen2.5-coder-14b-instruct-abliterated@q5_k_m` | Local LM Studio / vLLM / LocalAI endpoint. |

---

## 1.1 Frontier & Free Model Catalog

### A. Google Gemini Models
- `gemini-3.5-flash` *(Recommended / Default)*
- `gemini-3.5-flash-lite`
- `gemini-3.6-flash`
- `gemini-3.7-flash`
- `gemini-3.8-flash`
- `gemini-3.1-flash-lite`
- `gemini-3.1-pro-preview`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`
- `gemini-2.5-pro`

### B. OpenAI Frontier Models
- `gpt-5.6` *(Flagship / Highest Reasoning)*
- `gpt-5.5`
- `gpt-5`
- `gpt-4.5`
- `gpt-4o`

### C. Anthropic Frontier Models
- `claude-5-opus` *(Flagship Frontier)*
- `claude-4.5-sonnet`
- `claude-4-opus`
- `claude-3-7-sonnet`
- `claude-3-5-sonnet-20241022`

### D. DeepSeek Direct API
- `deepseek-reasoner` *(DeepSeek R1)*
- `deepseek-chat` *(DeepSeek V3)*

### E. Mistral AI & Cohere Models
- **Mistral**: `codestral-latest`, `mistral-large-latest`, `mistral-small-latest`
- **Cohere**: `command-r-plus`, `command-r7b-12-2024`

### F. Groq, Cerebras, Together AI, Fireworks & xAI (Grok)
- **Groq**: `deepseek-r1-distill-llama-70b`, `kimi-k2-instruct`, `llama-3.3-70b-versatile`
- **Cerebras**: `gpt-oss-120b`, `llama-3.3-70b`
- **Together AI**: `deepseek-ai/DeepSeek-R1`, `Qwen/Qwen2.5-Coder-32B-Instruct`, `meta-llama/Llama-3.3-70B-Instruct-Turbo`
- **Fireworks AI**: `accounts/fireworks/models/deepseek-r1`, `accounts/fireworks/models/qwen2p5-coder-32b-instruct`
- **xAI / Grok**: `grok-2-latest`, `grok-beta`
- **Perplexity**: `sonar-pro`, `sonar-reasoning-pro`

### G. OpenRouter Free Tier Examples
- `nvidia/nemotron-3-nano-30b-a3b:free` *(Very Fast / Lightweight)*
- `google/gemma-4-31b-it:free` *(Fast / Balanced)*
- `poolside/laguna-s-2.1:free` *(Fast / Coding-Focused)*
- `nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free` *(Fast / Reasoning)*
- `nvidia/nemotron-3-super-120b-a12b:free` *(Fast / High Quality)*
- `nvidia/nemotron-3-ultra-550b-a55b:free` *(Powerful / Deep Reasoning)*
- `openai/gpt-oss-20b:free` *(Capable / Slower)*

### H. Ollama & Local AI (LM Studio)
- **Ollama Cloud**: `qwen3-coder`, `gpt-oss:120b`, `deepseek-v3.1`
- **LM Studio / Local**: `qwen2.5-coder-14b-instruct-abliterated@q5_k_m`, `qwen3-14b-abliterated@q5_k_m`, `codestral-22b-v0.1-abliterated-v3`, `deepseek-coder-v2-lite-instruct@q5_k_m`


---

## 2. Setting Environment Variables & Running Outside an IDE (Exiting Antigravity)

When you exit Google Antigravity or any IDE and want to run **WinDbgMCP** with your choice of AI provider and API keys, you can run WinDbgMCP in **Standalone Stdio Mode** or **Standalone SSE HTTP Server Mode**.

### Step 1: Set Your Provider API Key

Set the environment variable corresponding to your preferred provider in your terminal session before launching:

#### A. Windows PowerShell
```powershell
# Google Gemini
$env:GEMINI_API_KEY="AIzaSyYourActualGoogleGeminiKeyHere"

# OpenAI
$env:OPENAI_API_KEY="sk-proj-YourActualOpenAIKeyHere"

# Anthropic Claude
$env:ANTHROPIC_API_KEY="sk-ant-YourActualAnthropicKeyHere"

# Groq / DeepSeek
$env:GROQ_API_KEY="gsk_your_groq_api_key"

# OpenRouter (Free & Paid Models)
$env:OPENROUTER_API_KEY="sk-or-v1-your_openrouter_key"
```

#### B. Windows Command Prompt (CMD)
```cmd
:: Google Gemini
set GEMINI_API_KEY=AIzaSyYourActualGoogleGeminiKeyHere

:: OpenAI
set OPENAI_API_KEY=sk-proj-YourActualOpenAIKeyHere

:: Anthropic Claude
set ANTHROPIC_API_KEY=sk-ant-YourActualAnthropicKeyHere
```

#### C. Permanent System-Wide Environment Variables (`setx`)
```cmd
:: Persist across all future terminal windows (restart prompt after running setx)
setx GEMINI_API_KEY "AIzaSyYourActualGoogleGeminiKeyHere"
setx OPENAI_API_KEY "sk-proj-YourActualOpenAIKeyHere"
setx ANTHROPIC_API_KEY "sk-ant-YourActualAnthropicKeyHere"
```

#### D. Linux / macOS Terminal (Bash / Zsh)
```bash
export GEMINI_API_KEY="AIzaSyYourActualGoogleGeminiKeyHere"
export OPENAI_API_KEY="sk-proj-YourActualOpenAIKeyHere"
export ANTHROPIC_API_KEY="sk-ant-YourActualAnthropicKeyHere"
```

---

### Step 2: Launching WinDbgMCP Outside an IDE

You have two choices for launching the server depending on your external consumer:

#### Mode A: Standalone Stdio Mode (Default for CLI Tools)
Use Stdio mode if you are invoking WinDbgMCP from command-line AI clients (Claude Code CLI, custom Python scripts, or command-line LLM runners):

```bash
# From WinDbgMCP root directory
python -m windbg_mcp
```

#### Mode B: Standalone SSE Network Mode (HTTP Server)
Use SSE mode if you want WinDbgMCP running as a background network service accessible via standard HTTP/JSON-RPC by external web apps, custom Python scripts, or remote LLM agents:

```bash
# Launch HTTP SSE server on port 8000
python -m windbg_mcp --sse --port 8000
```
Once launched, the server streams tools and endpoints live on `http://localhost:8000/sse`.

---

## 3. Configuring Environment Variables in IDEs & MCP Clients

When running `WinDbgMCP` inside an IDE or desktop MCP host (Google Antigravity, Cursor, Codex, VS Code, Claude Desktop), supply environment variables inside your MCP configuration JSON:

### A. Google Antigravity / Cursor / Codex / VS Code (`mcp.json` or `codex.mcp.json`)
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

## 4. Programmatic Python API & Custom Script Usage

If you exit Antigravity and write custom Python scripts or automated agents to interact with WinDbgMCP using your API key:

### Example A: Direct Python Server Initialization
```python
import os
from windbg_mcp.ai_provider import AIProviderConfig, get_available_ai_providers

# 1. Set or confirm your API key in code/environment
os.environ["GEMINI_API_KEY"] = "AIzaSyYourActualGoogleGeminiKeyHere"

# 2. Check provider availability status
status = get_available_ai_providers()
print(f"Gemini Status: {status['gemini']['status']}")  # Outputs: configured

# 3. Initialize AI provider configuration object
cfg = AIProviderConfig(provider="gemini", model="gemini-3.5-flash")
print(cfg.to_dict())
# Outputs:
# {
#   'provider': 'gemini',
#   'base_url': 'https://generativelanguage.googleapis.com',
#   'model': 'gemini-3.5-flash',
#   'api_key_set': True,
#   'masked_api_key': 'AIza...1234'
# }
```

### Example B: Programmatic Tool Execution in Custom Python Script
```python
import asyncio
from windbg_mcp.server import mcp

async def run_standalone_debugger():
    # Call any FastMCP tool programmatically without an IDE
    result = await mcp.call_tool("get_ai_provider_status", {})
    print(result)

if __name__ == "__main__":
    asyncio.run(run_standalone_debugger())
```

---

## 5. Quick-Start One-Liner Launcher Scripts

Create these quick shortcut scripts in your project root to start WinDbgMCP with your preferred provider outside of any IDE:

### `start_gemini.bat` (Windows Batch)
```cmd
@echo off
set GEMINI_API_KEY=AIzaSyYourActualGoogleGeminiKeyHere
python -m windbg_mcp
```

### `start_openai.ps1` (PowerShell)
```powershell
$env:OPENAI_API_KEY="sk-proj-YourActualOpenAIKeyHere"
python -m windbg_mcp
```

---

## 6. MCP Tools for AI Provider Management

WinDbgMCP exposes two dedicated FastMCP tools for AI provider inspection:

1. **`get_ai_provider_status`**: Returns Markdown table detailing all 11 providers, associated environment variables, and active configuration states.
2. **`configure_ai_provider(provider, model, base_url, api_key)`**: Dynamically validates and initializes an AI provider configuration object.
