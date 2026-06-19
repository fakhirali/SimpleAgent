#!/usr/bin/env python3
"""
A simplified AI agent that can read/write files and search the web.
Uses OpenAI-compatible Chat Completions API with tool calling.
"""
import json, os, sys
from openai import OpenAI

# Default configuration - can be overridden by environment variables
BASE_URL = os.environ.get("OPENAI_BASE_URL", "http://localhost:8000/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "not-required")
PROMPT_FILE = os.environ.get("PROMPT_FILE", "prompt.txt")

# ── Tool implementations ──────────────────────────────────────────

def load_prompt(filename=PROMPT_FILE):
    """Load the system prompt from a file."""
    try:
        with open(filename, 'r') as f:
            return f.read()
    except FileNotFoundError:
        # Default prompt if file not found
        return "You are a helpful assistant."
    except Exception as e:
        print(f"Warning: Could not load prompt from {filename}: {e}")
        return "You are a helpful assistant."

def run_command(command):
    import subprocess

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout
        if result.stderr:
            output += f"\nstderr:\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n(exit code: {result.returncode})"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {e}"

FUNCTIONS = {"run_command": run_command}

def strip_thinking(text):
    return text.rsplit("</think>", 1)[-1].lstrip() if "</think>" in text else text

# ── Tool schemas ──────────────────────────────────────────────────

TOOLS = [
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Run a CLI command on the user's machine",
        "parameters": {"type": "object", "properties": {"command": {"type": "string", "description": "The shell command to execute"}}, "required": ["command"]}}},
]

# ── Agent loop ────────────────────────────────────────────────────

def run_agent(messages, max_turns=10):
    """Run the agent loop: send messages, handle tool calls, repeat."""
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    for _ in range(max_turns):
        response = client.chat.completions.create(
            model="RedHatAI/Qwen3.5-4B-FP8-dynamic",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            extra_body={"chat_template_kwargs": {"enable_thinking": True}},
        )

        msg = response.choices[0].message

        # If the model wants to call tools, execute them
        if msg.tool_calls:
            # Print a single line of the tool call input
            print(f"Tool call: {msg.tool_calls[0].function.name}({msg.tool_calls[0].function.arguments})")

            # Append assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": msg.content or None,
                "tool_calls": [
                    {"id": tc.id, "type": "function", "function": tc.function.model_dump()}
                    for tc in msg.tool_calls
                ],
            })

            # Execute each tool and append the result
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments)
                result = FUNCTIONS[tc.function.name](**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
        else:
            # No tool calls → final answer
            content = strip_thinking(msg.content) if msg.content else msg.content
            if content:
                print(content)
                messages.append({"role": "assistant", "content": content})
            return

# ── CLI ───────────────────────────────────────────────────────────

def main():
    # Load the system prompt from the file
    system_prompt = load_prompt(PROMPT_FILE)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Please articulate your thoughts within your thinking block, then prepare your final answer in a separate block without introducing your thoughts in it."},
    ]

    if len(sys.argv) > 1:
        # One-shot mode
        messages.append({"role": "user", "content": " ".join(sys.argv[1:])})
        run_agent(messages)
    else:
        # Interactive REPL mode
        print("Agent ready. Type a task, /reset, or /exit.")
        while True:
            try:
                msg = input("> ").strip()
            except KeyboardInterrupt:
                print()
                return
            if msg in ("/exit", "/quit"):
                return
            if msg == "/reset":
                messages = messages[:2]
                print("Reset.")
                continue
            if not msg:
                continue
            messages.append({"role": "user", "content": msg})
            try:
                run_agent(messages)
            except KeyboardInterrupt:
                print("\nInterrupted.")
            print()

if __name__ == "__main__":
    main()
