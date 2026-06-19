# SimpleAgent

A Python AI agent that executes CLI commands and explores your system using OpenAI tool calling.

## 🚀 Quick Start

```bash
# Install
pip install -r requirements.txt

# Run interactively
uv run python3 agent.py

# Run one-command
uv run python3 agent.py "grep 'ERROR' app.py"
```

## ⚙️ Setup

```bash
# Optionally set environment variables
export OPENAI_API_KEY="your_key"
```

Features: CLI command execution, tool calling, thinking blocks, interactive mode.

For details: see `agent.py` and `.gitignore`.

## 📝 Instruction

**Important**: Within your thinking block, articulate your thoughts. Then prepare your final answer in a separate block without introducing your thoughts in it.
