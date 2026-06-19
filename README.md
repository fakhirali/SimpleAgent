# SimpleAI

A simplified AI agent that can interact with CLI commands and explore your system. Built with OpenAI-compatible Chat Completions API and tool calling.

## 🚀 Features

- **CLI Command Execution**: Run shell commands through the `run_command` tool
- **Tool Calling**: Supports OpenAI-style function calling with automatic tool execution
- **Thinking Blocks**: Enable deep reasoning before generating responses
- **Pure Python**: No complex build steps, just run `python3 agent.py`
- **Environment Support**: Customizable via environment variables
- **Flexible Usage**: Interactive mode or one-shot execution

## 📋 Installation

### Requirements

- Python 3.8+
- [openai SDK](https://pypi.org/project/openai/) (v2.0+)
- OpenAI-compatible API server

### Setup Steps

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables (optional):
   ```bash
   # Optional: Set your API key
   export OPENAI_API_KEY="your_api_key"
   export OPENAI_BASE_URL="http://localhost:8000/v1"  # Custom endpoint
   ```

## 🛠️ Usage

### Interactive Mode

Run the agent interactively:
```bash
uv run python3 agent.py
```

Available commands:
- `> command` - Send a natural language query
- `/reset` - Reset conversation history
- `/exit` - Exit the agent
- Empty line - Press Enter to submit

**Example**:
```bash
> What files exist in my project directory?
> Write a Python script that allows internet browsing
> /reset
> List daily tasks
```

### One-Shot Mode

Run a single query and get the result:
```bash
uv run python3 agent.py "grep 'ERROR' app.py"
```

The agent will execute the command and show the output.

### Custom Prompt

Replace `prompt.txt` with your own system instructions:
```bash
PROMPT_FILE=custom_prompt.txt uv run python3 agent.py <your-query>
```

## ⚙️ Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `not-required` | Your API key for the OpenAI-compatible endpoint |
| `OPENAI_BASE_URL` | `http://localhost:8000/v1` | Custom API endpoint |
| `PROMPT_FILE` | `prompt.txt` | Path to system prompt file |

## 🔧 Tool Schema

The `run_command` tool allows the agent to execute shell commands:

```json
{
  "type": "function",
  "function": {
    "name": "run_command",
    "description": "Run a CLI command on the user's machine",
    "parameters": {
      "type": "object",
      "properties": {
        "command": {
          "type": "string",
          "description": "The shell command to execute"
        }
      },
      "required": ["command"]
    }
  }
}
```

## 🤝 Security Notes

⚠️ **Important Considerations:**

1. **Command Execution**: The agent executes shell commands. Restrict permissions or use a sandbox when `OPENAI_API_KEY` is not set.

2. **API Keys**: Store sensitive credentials securely. Never commit them to version control.

3. **Permissions**: Limit the agent's environment access based on deployment requirements.

4. **Timeout**: Commands are limited to 10 seconds to prevent long-running operations.

## 📄 License

This project is open source. Feel free to modify and extend as needed.

## 🎯 Example Use Cases

- **Exploration**: List directories, view file contents, search logs
- **Development**: Run tests, clean code, restart services
- **Debugging**: Analyze error messages, test commands
- **Automation**: Generate scripts, automate repetitive tasks
- **Research**: Fetch and analyze files in research repositories

---

Enjoy exploring with your AI agent! 🚀
