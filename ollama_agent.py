#!/usr/bin/env python3
"""ollama_cli_agent.py

A more professional, "slick" command-line chat client for Ollama.

Highlights
- Interactive REPL with slash-commands (/help, /models, /model, /pull, /clear, /save, /load, /exit)
- Streaming responses with optional Rich formatting (auto-falls back to plain text)
- Config file stored in ~/.ollama_cli_agent.json (theme + default model)
- Session save/load to ~/.ollama_cli_agent_sessions/<name>.json
- Sensible error messages when Ollama isn't running or a model is missing

Requirements
- Python 3.9+
- ollama (pip install ollama)
- Optional: rich (pip install rich) for nicer output

Run
  python ollama_cli_agent.py
  python ollama_cli_agent.py --model llama3.2

Notes
- This stays fully Ollama-based; it does not replace your backend.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import ollama


# -----------------------------
# Optional Rich UI
# -----------------------------

def _rich() -> Tuple[bool, Any, Any, Any, Any, Any]:
    """Return (enabled, console, Text, Panel, box, live).

    Importing rich can fail; in that case we fall back to plain output.
    """

    try:
        from rich.console import Console
        from rich.text import Text
        from rich.panel import Panel
        from rich import box
        from rich.live import Live

        # disable Rich if piping to file / non-interactive
        enabled = sys.stdout.isatty()
        return enabled, Console(), Text, Panel, box, Live
    except Exception:
        return False, None, None, None, None, None


RICH_ENABLED, CONSOLE, RichText, RichPanel, RichBox, RichLive = _rich()


def println(s: str = "") -> None:
    if RICH_ENABLED:
        CONSOLE.print(s)
    else:
        print(s)


def warn(s: str) -> None:
    # Use ASCII markers for maximum terminal compatibility.
    if RICH_ENABLED:
        CONSOLE.print(f"[yellow][!] {s}[/yellow]")
    else:
        print(f"WARNING: {s}")


def err(s: str) -> None:
    # Use ASCII markers for maximum terminal compatibility.
    if RICH_ENABLED:
        CONSOLE.print(f"[red][X] {s}[/red]")
    else:
        print(f"ERROR: {s}")


# -----------------------------
# Storage
# -----------------------------

APP_DIR = Path.home() / ".ollama_cli_agent"
CONFIG_PATH = APP_DIR / "config.json"
SESSIONS_DIR = APP_DIR / "sessions"


def _safe_mkdir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


@dataclass
class Config:
    default_model: str = "llama3.2"
    system_prompt: str = "You are a helpful assistant."


def load_config() -> Config:
    try:
        if CONFIG_PATH.exists():
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            return Config(
                default_model=str(data.get("default_model", Config.default_model)),
                system_prompt=str(data.get("system_prompt", Config.system_prompt)),
            )
    except Exception:
        # best effort; don't crash on config
        pass
    return Config()


def save_config(cfg: Config) -> None:
    try:
        _safe_mkdir(APP_DIR)
        CONFIG_PATH.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")
    except Exception as e:
        warn(f"Couldn't save config: {e}")


# -----------------------------
# Ollama helpers
# -----------------------------


def list_models() -> List[str]:
    """Return installed model names."""
    resp = ollama.list()

    # The python client has changed shapes across versions.
    models: List[str] = []

    if isinstance(resp, dict):
        items = resp.get("models", []) or []
    else:
        items = getattr(resp, "models", None) or []

    for it in items:
        if isinstance(it, str):
            models.append(it)
            continue
        if isinstance(it, dict):
            name = it.get("name") or it.get("model")
            tag = it.get("tag")
            if name and tag and ":" not in str(name):
                name = f"{name}:{tag}"
            if name:
                models.append(str(name))
            continue
        name = getattr(it, "name", None) or getattr(it, "model", None)
        tag = getattr(it, "tag", None)
        if name and tag and ":" not in str(name):
            name = f"{name}:{tag}"
        if name:
            models.append(str(name))

    # de-dupe but stable
    seen = set()
    out: List[str] = []
    for m in models:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


def model_exists(model: str) -> bool:
    installed = list_models()
    if model in installed:
        return True
    if ":" not in model and f"{model}:latest" in installed:
        return True
    return False


def normalize_model(model: str) -> str:
    if model_exists(model):
        return model
    if ":" not in model and model_exists(f"{model}:latest"):
        return f"{model}:latest"
    return model


def pull_model(model: str) -> None:
    model = model.strip()
    if not model:
        err("No model provided")
        return

    println(f"Downloading: {model}")

    if RICH_ENABLED:
        # A tiny status line that updates as bytes move.
        from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn

        progress = Progress(
            TextColumn("{task.description}"),
            BarColumn(),
            TextColumn("{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
        )
        task_id = progress.add_task(f"pull {model}", total=100)

        with progress:
            last_pct = 0.0
            for ev in ollama.pull(model, stream=True):
                status = str(ev.get("status", ""))
                completed = float(ev.get("completed") or 0)
                total = float(ev.get("total") or 0)
                pct = (completed / total * 100.0) if total else last_pct
                last_pct = pct
                progress.update(task_id, completed=min(100.0, pct), description=f"{status}")

    else:
        for ev in ollama.pull(model, stream=True):
            status = ev.get("status", "")
            completed = ev.get("completed")
            total = ev.get("total")
            if completed and total:
                pct = int(float(completed) / float(total) * 100)
                print(f"{status} ({pct}%)")
            else:
                print(status)


# -----------------------------
# Session
# -----------------------------


def save_session(name: str, history: List[Dict[str, str]]) -> Path:
    _safe_mkdir(SESSIONS_DIR)
    path = SESSIONS_DIR / f"{name}.json"
    payload = {
        "name": name,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "history": history,
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def load_session(name: str) -> List[Dict[str, str]]:
    path = SESSIONS_DIR / f"{name}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    hist = data.get("history", [])
    if not isinstance(hist, list):
        raise ValueError("Invalid session format")
    out: List[Dict[str, str]] = []
    for m in hist:
        if isinstance(m, dict) and "role" in m and "content" in m:
            out.append({"role": str(m["role"]), "content": str(m["content"])})
    return out


# -----------------------------
# REPL
# -----------------------------

HELP = """\
Commands:
  /help                     Show this help
  /models                   List installed models
  /model <name|auto>        Set model for this session (does not pull)
  /pull <name>              Download a model via Ollama
  /system <text>            Set system prompt for this session
  /clear                    Clear chat history
  /save <name>              Save session history
  /load <name>              Load session history
  /exit                     Quit

Tips:
- Paste multi-line prompts by starting with three double-quotes, and ending with three double-quotes on its own line.
- Use --model to start with a specific model.
"""


def _read_multiline(first_line: str) -> str:
    """Support triple-quote multi-line entry."""
    if first_line.strip() != '"""':
        return first_line

    lines: List[str] = []
    while True:
        try:
            line = input("... ")
        except EOFError:
            break
        if line.strip() == '"""':
            break
        lines.append(line)
    return "\n".join(lines)


def stream_chat(model: str, messages: List[Dict[str, str]]) -> str:
    """Stream response; return the full text."""
    full: List[str] = []

    if RICH_ENABLED:
        # Render assistant output as it arrives.
        from rich.markdown import Markdown

        println()  # spacing
        with RichLive(refresh_per_second=16) as live:
            buf = ""
            for chunk in ollama.chat(model=model, messages=messages, stream=True):
                piece = chunk.get("message", {}).get("content", "")
                if not piece:
                    continue
                full.append(piece)
                buf += piece
                live.update(Markdown(buf))
        println()
    else:
        for chunk in ollama.chat(model=model, messages=messages, stream=True):
            piece = chunk.get("message", {}).get("content", "")
            if not piece:
                continue
            full.append(piece)
            sys.stdout.write(piece)
            sys.stdout.flush()
        print("\n")

    return "".join(full)


def print_header(title: str, subtitle: str) -> None:
    if RICH_ENABLED:
        panel = RichPanel(
            f"[bold]{title}[/bold]\n[dim]{subtitle}[/dim]",
            box=RichBox.ROUNDED,
            padding=(1, 2),
        )
        CONSOLE.print(panel)
    else:
        print(title)
        print(subtitle)
        print("-" * max(10, len(title)))


def repl(cfg: Config, model: str, system_prompt: str) -> None:
    model_mode = model
    history: List[Dict[str, str]] = []

    print_header(
        "Ollama CLI Agent",
        f"Model: {model_mode} | Sessions: {SESSIONS_DIR} | Config: {CONFIG_PATH}",
    )
    println("Type /help for commands. Ctrl+C to cancel input, Ctrl+D to quit.")

    def effective_model() -> str:
        # 'auto' chooses default model. We don't do smart routing here;
        # if you want routing, it can be added cleanly.
        if model_mode == "auto":
            return normalize_model(cfg.default_model)
        return normalize_model(model_mode)

    while True:
        try:
            line = input("you> ")
        except KeyboardInterrupt:
            println()  # just a new line
            continue
        except EOFError:
            println("\nbye")
            return

        text = _read_multiline(line).strip()
        if not text:
            continue

        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1].strip() if len(parts) > 1 else ""

            if cmd in ("/exit", "/quit"):
                println("bye")
                return
            if cmd == "/help":
                println(HELP)
                continue
            if cmd == "/models":
                try:
                    ms = list_models()
                except Exception as e:
                    err(f"Couldn't list models. Is Ollama running? ({e})")
                    continue
                if not ms:
                    warn("No installed models found.")
                else:
                    println("Installed models:")
                    for m in ms:
                        println(f"  - {m}")
                continue
            if cmd == "/model":
                if not arg:
                    warn("Usage: /model <name|auto>")
                    continue
                model_mode = arg
                println(f"Model set to: {model_mode}")
                continue
            if cmd == "/pull":
                if not arg:
                    warn("Usage: /pull <name>")
                    continue
                try:
                    pull_model(arg)
                except Exception as e:
                    err(f"Pull failed: {e}")
                continue
            if cmd == "/system":
                if not arg:
                    warn("Usage: /system <text>")
                    continue
                system_prompt = arg
                println("System prompt updated for this session.")
                continue
            if cmd == "/clear":
                history.clear()
                println("History cleared.")
                continue
            if cmd == "/save":
                if not arg:
                    warn("Usage: /save <name>")
                    continue
                try:
                    path = save_session(arg, history)
                    println(f"Saved to: {path}")
                except Exception as e:
                    err(f"Save failed: {e}")
                continue
            if cmd == "/load":
                if not arg:
                    warn("Usage: /load <name>")
                    continue
                try:
                    history[:] = load_session(arg)
                    println(f"Loaded session: {arg} ({len(history)} messages)")
                except Exception as e:
                    err(f"Load failed: {e}")
                continue

            warn(f"Unknown command: {cmd}. Try /help")
            continue

        # Normal chat
        model_name = effective_model()
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(history)
        messages.append({"role": "user", "content": text})

        try:
            if not model_exists(model_name):
                warn(
                    f"Model '{model_name}' not found locally. Use /models to list or /pull {model_name} to download."
                )
            println(f"assistant[{model_name}]>")
            response = stream_chat(model_name, messages)

            history.append({"role": "user", "content": text})
            history.append({"role": "assistant", "content": response})

        except Exception as e:
            err(
                "Chat failed. Common causes: Ollama not running, model name wrong, or the model crashed.\n"
                f"Details: {e}"
            )


# -----------------------------
# Entry point
# -----------------------------


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="ollama-cli-agent",
        description="A slick interactive CLI chat client for Ollama.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              ollama-cli-agent
              ollama-cli-agent --model llama3.2
              ollama-cli-agent --model auto
            """
        ),
    )
    p.add_argument(
        "--model",
        default=None,
        help="Model to use (e.g. llama3.2, qwen2.5:7b). Use 'auto' for config default.",
    )
    p.add_argument(
        "--system",
        default=None,
        help="System prompt for this run (overrides config).",
    )
    p.add_argument(
        "--set-default-model",
        default=None,
        help="Update config default model and exit.",
    )
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    _safe_mkdir(APP_DIR)
    _safe_mkdir(SESSIONS_DIR)

    cfg = load_config()
    args = parse_args(argv)

    if args.set_default_model:
        cfg.default_model = str(args.set_default_model).strip() or cfg.default_model
        save_config(cfg)
        println(f"Default model saved: {cfg.default_model}")
        return 0

    model = (args.model or "auto").strip()
    system_prompt = (args.system if args.system is not None else cfg.system_prompt)

    try:
        repl(cfg=cfg, model=model, system_prompt=system_prompt)
        return 0
    except KeyboardInterrupt:
        println("\nbye")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())