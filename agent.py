#!/usr/bin/env python3
"""
AI agent with CLI access via tool calling.
"""
import json, os, sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://opencode.ai/zen/go/v1")
API_KEY = os.environ.get("OPENCODE_GO_API_KEY", "not-required")
PROMPT_FILE = os.environ.get("PROMPT_FILE", "prompt.txt")

def load_prompt(filename=PROMPT_FILE):
    try:
        return open(filename).read()
    except:
        return "You are a helpful assistant."

def run_command(command, timeout=60):
    import subprocess

    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
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

TOOLS = [
    {"type": "function", "function": {
        "name": "run_command",
        "description": "Run a CLI command on the user's machine",
        "parameters": {"type": "object", "properties": {
            "command": {"type": "string", "description": "The shell command to execute"},
            "timeout": {"type": "number", "description": "Timeout in seconds (default: 60)"}
        }, "required": ["command"]}}},
]

def run_agent(messages):
    """Run the agent loop: send messages, handle tool calls, repeat."""
    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    # Strip orphaned assistant tool_calls from interrupted runs
    while messages and "tool_calls" in messages[-1]:
        messages.pop()

    while True:
        stream = client.chat.completions.create(
            model="deepseek-v4-flash",
            messages=messages,
            tools=TOOLS,
            reasoning_effort="max",
            extra_body={"thinking": {"type": "enabled"}},
            stream=True,
        )

        content = ""
        tool_call_deltas = {}
        reasoning_shown = False

        for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            rc = getattr(delta, "reasoning_content", None)
            if rc:
                if not reasoning_shown:
                    print("─── reasoning ───", flush=True)
                    reasoning_shown = True
                print(rc, end="", flush=True)
                content += rc

            if delta.content:
                if reasoning_shown:
                    print("\n─── answer ───", flush=True)
                    reasoning_shown = False
                print(delta.content, end="", flush=True)
                content += delta.content

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    i = tc.index
                    if i not in tool_call_deltas:
                        tool_call_deltas[i] = {"id": "", "function": {"name": "", "arguments": ""}}
                    if tc.id:
                        tool_call_deltas[i]["id"] += tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_call_deltas[i]["function"]["name"] += tc.function.name
                        if tc.function.arguments:
                            tool_call_deltas[i]["function"]["arguments"] += tc.function.arguments

        print()

        if tool_call_deltas:
            print("─── tool call ───")
            tool_calls_list = [
                {
                    "id": tool_call_deltas[i]["id"],
                    "type": "function",
                    "function": {
                        "name": tool_call_deltas[i]["function"]["name"],
                        "arguments": tool_call_deltas[i]["function"]["arguments"],
                    },
                }
                for i in sorted(tool_call_deltas)
            ]
            print(f"{tool_calls_list[0]['function']['name']}({tool_calls_list[0]['function']['arguments']})")

            messages.append({
                "role": "assistant",
                "content": content or None,
                "tool_calls": tool_calls_list,
            })

            for tc_data in tool_calls_list:
                args = json.loads(tc_data["function"]["arguments"])
                result = FUNCTIONS[tc_data["function"]["name"]](**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc_data["id"],
                    "content": result,
                })
        else:
            if content:
                messages.append({"role": "assistant", "content": content})
            return

def main():
    # Load the system prompt from the file
    system_prompt = load_prompt(PROMPT_FILE)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Think step by step before answering."},
    ]

    if len(sys.argv) > 1:
        messages.append({"role": "user", "content": " ".join(sys.argv[1:])})
        run_agent(messages)
    else:
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
