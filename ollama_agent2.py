#!/usr/bin/env python3
"""ollama_gui_agent.py

A chat client for Ollama with both CLI and GUI modes.

Requirements:
    Python 3.9+
    ollama (pip install ollama)

Run:
    python ollama_gui_agent.py             # GUI mode
    python ollama_gui_agent.py --cli       # CLI mode
    python ollama_gui_agent.py --model llama3.2
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Optional


import ollama

# ─────────────────────────────────────────────
# Config & Storage
# ─────────────────────────────────────────────

APP_DIR = Path.home() / ".ollama_chat_agent"
CONFIG_PATH = APP_DIR / "config.json"
SESSIONS_DIR = APP_DIR / "sessions"


@dataclass
class Config:
    default_model: str = "llama3.2"
    system_prompt: str = "You are a helpful assistant."
    theme: str = "dark"
    font_size: int = 12

    @classmethod
    def load(cls) -> Config:
        try:
            if CONFIG_PATH.exists():
                data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
                return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        except Exception:
            pass
        return cls()

    def save(self) -> None:
        try:
            APP_DIR.mkdir(parents=True, exist_ok=True)
            CONFIG_PATH.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        except Exception as e:
            print(f"Warning: Couldn't save config: {e}")


# ─────────────────────────────────────────────
# Ollama Helpers
# ─────────────────────────────────────────────

class OllamaClient:
    """Thin wrapper around the ollama library for cleaner access."""

    @staticmethod
    def list_models() -> list[str]:
        resp = ollama.list()
        items = resp.get("models", []) if isinstance(resp, dict) else getattr(resp, "models", []) or []
        models: list[str] = []
        seen: set[str] = set()

        for item in items:
            name = None
            if isinstance(item, str):
                name = item
            elif isinstance(item, dict):
                name = item.get("name") or item.get("model")
                tag = item.get("tag")
                if name and tag and ":" not in str(name):
                    name = f"{name}:{tag}"
            else:
                name = getattr(item, "name", None) or getattr(item, "model", None)
                tag = getattr(item, "tag", None)
                if name and tag and ":" not in str(name):
                    name = f"{name}:{tag}"

            if name and str(name) not in seen:
                seen.add(str(name))
                models.append(str(name))
        return models

    @staticmethod
    def model_exists(model: str) -> bool:
        installed = OllamaClient.list_models()
        return model in installed or (
            ":" not in model and f"{model}:latest" in installed
        )

    @staticmethod
    def normalize(model: str) -> str:
        if OllamaClient.model_exists(model):
            return model
        if ":" not in model and OllamaClient.model_exists(f"{model}:latest"):
            return f"{model}:latest"
        return model

    @staticmethod
    def stream_chat(model: str, messages: list[dict], on_token=None) -> str:
        full: list[str] = []
        for chunk in ollama.chat(model=model, messages=messages, stream=True):
            piece = chunk.get("message", {}).get("content", "")
            if piece:
                full.append(piece)
                if on_token:
                    on_token(piece)
        return "".join(full)

    @staticmethod
    def pull(model: str, on_progress=None) -> None:
        for ev in ollama.pull(model, stream=True):
            if on_progress:
                status = str(ev.get("status", ""))
                completed = float(ev.get("completed") or 0)
                total = float(ev.get("total") or 1)
                on_progress(status, completed / total)


# ─────────────────────────────────────────────
# Session Management
# ─────────────────────────────────────────────

@dataclass
class Session:
    history: list[dict] = field(default_factory=list)
    name: str = "untitled"

    def add(self, role: str, content: str) -> None:
        self.history.append({"role": role, "content": content})

    def clear(self) -> None:
        self.history.clear()

    def build_messages(self, system_prompt: str, user_text: str) -> list[dict]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.history)
        messages.append({"role": "user", "content": user_text})
        return messages

    def save(self, name: str) -> Path:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        path = SESSIONS_DIR / f"{name}.json"
        payload = {
            "name": name,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
            "history": self.history,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.name = name
        return path

    @classmethod
    def load(cls, name: str) -> Session:
        path = SESSIONS_DIR / f"{name}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        hist = data.get("history", [])
        session = cls(name=name)
        for m in hist:
            if isinstance(m, dict) and "role" in m and "content" in m:
                session.history.append({"role": str(m["role"]), "content": str(m["content"])})
        return session

    @staticmethod
    def list_saved() -> list[str]:
        if not SESSIONS_DIR.exists():
            return []
        return [p.stem for p in SESSIONS_DIR.glob("*.json")]


# ─────────────────────────────────────────────
# GUI
# ─────────────────────────────────────────────

class ChatGUI:
    DARK = {
        "bg": "#1e1e2e",
        "fg": "#cdd6f4",
        "input_bg": "#313244",
        "input_fg": "#cdd6f4",
        "user_fg": "#89b4fa",
        "assistant_fg": "#a6e3a1",
        "system_fg": "#f9e2af",
        "error_fg": "#f38ba8",
        "button_bg": "#45475a",
        "accent": "#cba6f7",
    }
    LIGHT = {
        "bg": "#eff1f5",
        "fg": "#4c4f69",
        "input_bg": "#ffffff",
        "input_fg": "#4c4f69",
        "user_fg": "#1e66f5",
        "assistant_fg": "#40a02b",
        "system_fg": "#df8e1d",
        "error_fg": "#d20f39",
        "button_bg": "#ccd0da",
        "accent": "#8839ef",
    }

    def __init__(self, config: Config, model: str, system_prompt: str):
        self.config = config
        self.model = model
        self.system_prompt = system_prompt
        self.session = Session()
        self.is_generating = False
        self.colors = self.DARK if config.theme == "dark" else self.LIGHT

        self.root = tk.Tk()
        self.root.title("Ollama Chat")
        self.root.geometry("900x700")
        self.root.minsize(600, 400)
        self.root.configure(bg=self.colors["bg"])

        self._build_ui()
        self._bind_keys()
        self._show_welcome()

    def _build_ui(self) -> None:
        c = self.colors

        # Create status_var FIRST so _refresh_models can use it
        self.status_var = tk.StringVar(value="Ready")

        # ── Top bar ──
        top = tk.Frame(self.root, bg=c["bg"], padx=10, pady=5)
        top.pack(fill=tk.X)

        tk.Label(top, text="Model:", bg=c["bg"], fg=c["fg"],
                 font=("Segoe UI", 10)).pack(side=tk.LEFT)

        self.model_var = tk.StringVar(value=self.model)
        self.model_combo = ttk.Combobox(top, textvariable=self.model_var, width=25,
                                         state="readonly")
        self.model_combo.pack(side=tk.LEFT, padx=(5, 10))
        self._refresh_models()

        btn_style = {"bg": c["button_bg"], "fg": c["fg"], "relief": "flat",
                     "padx": 8, "pady": 3, "font": ("Segoe UI", 9)}

        tk.Button(top, text="⟳ Refresh", command=self._refresh_models, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Pull Model", command=self._pull_dialog, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Clear Chat", command=self._clear_chat, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Save", command=self._save_dialog, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Load", command=self._load_dialog, **btn_style).pack(side=tk.LEFT, padx=2)
        tk.Button(top, text="Settings", command=self._settings_dialog, **btn_style).pack(side=tk.LEFT, padx=2)

        # ── Chat display ──
        chat_frame = tk.Frame(self.root, bg=c["bg"], padx=10, pady=5)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg=c["bg"],
            fg=c["fg"],
            font=("Consolas", self.config.font_size),
            insertbackground=c["fg"],
            relief="flat",
            state=tk.DISABLED,
            cursor="arrow",
            padx=10,
            pady=10,
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Tags for colored text
        self.chat_display.tag_config("user", foreground=c["user_fg"], font=("Consolas", self.config.font_size, "bold"))
        self.chat_display.tag_config("assistant", foreground=c["assistant_fg"])
        self.chat_display.tag_config("system", foreground=c["system_fg"], font=("Consolas", self.config.font_size - 1))
        self.chat_display.tag_config("error", foreground=c["error_fg"])
        self.chat_display.tag_config("label", foreground=c["accent"], font=("Consolas", self.config.font_size, "bold"))

        # ── Input area ──
        input_frame = tk.Frame(self.root, bg=c["bg"], padx=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))

        self.input_box = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            bg=c["input_bg"],
            fg=c["input_fg"],
            font=("Consolas", self.config.font_size),
            insertbackground=c["input_fg"],
            relief="flat",
            padx=8,
            pady=8,
        )
        self.input_box.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.send_btn = tk.Button(
            input_frame,
            text="Send ⏎",
            command=self._on_send,
            bg=c["accent"],
            fg="#1e1e2e",
            font=("Segoe UI", 11, "bold"),
            relief="flat",
            padx=16,
            pady=8,
            cursor="hand2",
        )
        self.send_btn.pack(side=tk.RIGHT)

        # ── Status bar ──
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            bg=c["button_bg"], fg=c["fg"],
            font=("Segoe UI", 9), anchor="w", padx=10, pady=2,
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _bind_keys(self) -> None:
        self.input_box.bind("<Return>", self._on_enter)
        self.input_box.bind("<Shift-Return>", lambda e: None)  # allow newlines

    def _on_enter(self, event) -> str:
        if not self.is_generating:
            self.root.after(10, self._on_send)
        return "break"  # prevent newline insertion

    def _append_chat(self, text: str, tag: str = "") -> None:
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, text, tag)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def _show_welcome(self) -> None:
        self._append_chat("Welcome to Ollama Chat!\n", "label")
        self._append_chat(f"Model: {self.model} | System: {self.system_prompt[:50]}...\n", "system")
        self._append_chat("Type a message below and press Enter to chat.\n\n", "system")

    def _refresh_models(self) -> None:
        try:
            models = OllamaClient.list_models()
            self.model_combo["values"] = models
            if models and self.model_var.get() not in models:
                normalized = OllamaClient.normalize(self.model_var.get())
                if normalized in models:
                    self.model_var.set(normalized)
                else:
                    self.model_var.set(models[0])
            self.status_var.set(f"Found {len(models)} model(s)")
        except ConnectionError:
            self.model_combo["values"] = [self.model_var.get()]
            self.status_var.set("⚠ Ollama not running — start it and click Refresh")
        except Exception as e:
            self.model_combo["values"] = [self.model_var.get()]
            self.status_var.set(f"Error: {e}")

    def _on_send(self) -> None:
        text = self.input_box.get("1.0", tk.END).strip()
        if not text or self.is_generating:
            return

        self.input_box.delete("1.0", tk.END)
        model = OllamaClient.normalize(self.model_var.get())

        # Display user message
        self._append_chat("You:\n", "label")
        self._append_chat(f"{text}\n\n", "user")

        # Check model exists
        if not OllamaClient.model_exists(model):
            self._append_chat(f"⚠ Model '{model}' not found. Use Pull Model to download it.\n\n", "error")
            return

        messages = self.session.build_messages(self.system_prompt, text)

        # Display assistant label
        self._append_chat(f"Assistant [{model}]:\n", "label")

        self.is_generating = True
        self.send_btn.config(state=tk.DISABLED, text="...")
        self.status_var.set(f"Generating with {model}...")

        def generate():
            try:
                full_response = OllamaClient.stream_chat(
                    model, messages,
                    on_token=lambda token: self.root.after(0, self._append_chat, token, "assistant")
                )
                self.session.add("user", text)
                self.session.add("assistant", full_response)
                self.root.after(0, self._append_chat, "\n\n", "")
                self.root.after(0, self._generation_done, None)
            except Exception as e:
                self.root.after(0, self._append_chat, f"\n⚠ Error: {e}\n\n", "error")
                self.root.after(0, self._generation_done, str(e))

        threading.Thread(target=generate, daemon=True).start()

    def _generation_done(self, error: Optional[str]) -> None:
        self.is_generating = False
        self.send_btn.config(state=tk.NORMAL, text="Send ⏎")
        self.status_var.set("Ready" if not error else f"Error: {error}")

    def _clear_chat(self) -> None:
        self.session.clear()
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self._show_welcome()
        self.status_var.set("Chat cleared")

    def _pull_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Pull Model")
        dialog.geometry("400x150")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)

        tk.Label(dialog, text="Model name:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Segoe UI", 11)).pack(pady=(15, 5))

        entry = tk.Entry(dialog, width=30, font=("Consolas", 12),
                         bg=self.colors["input_bg"], fg=self.colors["input_fg"],
                         insertbackground=self.colors["input_fg"])
        entry.pack(pady=5)
        entry.focus()

        progress_var = tk.StringVar(value="")
        progress_label = tk.Label(dialog, textvariable=progress_var,
                                  bg=self.colors["bg"], fg=self.colors["system_fg"],
                                  font=("Segoe UI", 9))
        progress_label.pack(pady=5)

        def do_pull():
            name = entry.get().strip()
            if not name:
                return

            def run():
                try:
                    OllamaClient.pull(
                        name,
                        on_progress=lambda s, p: self.root.after(
                            0, progress_var.set, f"{s} ({p:.0%})"
                        )
                    )
                    self.root.after(0, self._refresh_models)
                    self.root.after(0, progress_var.set, "Done!")
                    self.root.after(0, self.status_var.set, f"Pulled {name}")
                except Exception as e:
                    self.root.after(0, progress_var.set, f"Error: {e}")

            threading.Thread(target=run, daemon=True).start()

        tk.Button(dialog, text="Pull", command=do_pull,
                  bg=self.colors["accent"], fg="#1e1e2e",
                  font=("Segoe UI", 10, "bold"), relief="flat",
                  padx=16).pack(pady=5)

    def _save_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Session")
        dialog.geometry("350x120")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)

        tk.Label(dialog, text="Session name:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Segoe UI", 11)).pack(pady=(15, 5))

        entry = tk.Entry(dialog, width=25, font=("Consolas", 12),
                         bg=self.colors["input_bg"], fg=self.colors["input_fg"],
                         insertbackground=self.colors["input_fg"])
        entry.insert(0, self.session.name)
        entry.pack(pady=5)
        entry.focus()

        def do_save():
            name = entry.get().strip()
            if name:
                try:
                    path = self.session.save(name)
                    self.status_var.set(f"Saved: {path}")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Save Error", str(e))

        tk.Button(dialog, text="Save", command=do_save,
                  bg=self.colors["accent"], fg="#1e1e2e",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16).pack(pady=5)

    def _load_dialog(self) -> None:
        saved = Session.list_saved()
        if not saved:
            messagebox.showinfo("Load", "No saved sessions found.")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Load Session")
        dialog.geometry("350x200")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)

        tk.Label(dialog, text="Select session:", bg=self.colors["bg"], fg=self.colors["fg"],
                 font=("Segoe UI", 11)).pack(pady=(15, 5))

        listbox = tk.Listbox(dialog, font=("Consolas", 11),
                             bg=self.colors["input_bg"], fg=self.colors["input_fg"],
                             selectbackground=self.colors["accent"])
        for s in saved:
            listbox.insert(tk.END, s)
        listbox.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)

        def do_load():
            sel = listbox.curselection()
            if not sel:
                return
            name = saved[sel[0]]
            try:
                self.session = Session.load(name)
                self._clear_chat()
                # Replay history in display
                for msg in self.session.history:
                    role = msg["role"]
                    if role == "user":
                        self._append_chat("You:\n", "label")
                        self._append_chat(f"{msg['content']}\n\n", "user")
                    elif role == "assistant":
                        self._append_chat("Assistant:\n", "label")
                        self._append_chat(f"{msg['content']}\n\n", "assistant")
                self.status_var.set(f"Loaded: {name} ({len(self.session.history)} messages)")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Load Error", str(e))

        tk.Button(dialog, text="Load", command=do_load,
                  bg=self.colors["accent"], fg="#1e1e2e",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16).pack(pady=5)

    def _settings_dialog(self) -> None:
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings")
        dialog.geometry("450x300")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)

        lbl_opts = {"bg": self.colors["bg"], "fg": self.colors["fg"], "font": ("Segoe UI", 10), "anchor": "w"}
        entry_opts = {"font": ("Consolas", 11), "bg": self.colors["input_bg"],
                      "fg": self.colors["input_fg"], "insertbackground": self.colors["input_fg"]}

        # System prompt
        tk.Label(dialog, text="System Prompt:", **lbl_opts).pack(fill=tk.X, padx=15, pady=(15, 2))
        sys_entry = tk.Text(dialog, height=3, wrap=tk.WORD, **entry_opts)
        sys_entry.insert("1.0", self.system_prompt)
        sys_entry.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Default model
        tk.Label(dialog, text="Default Model:", **lbl_opts).pack(fill=tk.X, padx=15, pady=(0, 2))
        model_entry = tk.Entry(dialog, **entry_opts)
        model_entry.insert(0, self.config.default_model)
        model_entry.pack(fill=tk.X, padx=15, pady=(0, 10))

        # Theme
        tk.Label(dialog, text="Theme:", **lbl_opts).pack(fill=tk.X, padx=15, pady=(0, 2))
        theme_var = tk.StringVar(value=self.config.theme)
        theme_frame = tk.Frame(dialog, bg=self.colors["bg"])
        theme_frame.pack(fill=tk.X, padx=15)
        tk.Radiobutton(theme_frame, text="Dark", variable=theme_var, value="dark",
                       bg=self.colors["bg"], fg=self.colors["fg"], selectcolor=self.colors["input_bg"]).pack(side=tk.LEFT)
        tk.Radiobutton(theme_frame, text="Light", variable=theme_var, value="light",
                       bg=self.colors["bg"], fg=self.colors["fg"], selectcolor=self.colors["input_bg"]).pack(side=tk.LEFT)

        def do_save():
            self.system_prompt = sys_entry.get("1.0", tk.END).strip()
            self.config.default_model = model_entry.get().strip()
            self.config.theme = theme_var.get()
            self.config.save()
            self.status_var.set("Settings saved (restart for theme change)")
            dialog.destroy()

        tk.Button(dialog, text="Save Settings", command=do_save,
                  bg=self.colors["accent"], fg="#1e1e2e",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=16).pack(pady=15)

    def run(self) -> None:
        self.root.mainloop()


# ─────────────────────────────────────────────
# CLI REPL (kept for --cli mode)
# ─────────────────────────────────────────────

HELP = """\
Commands:
  /help              Show this help
  /models            List installed models
  /model <name>      Set model
  /pull <name>       Download a model
  /system <text>     Set system prompt
  /clear             Clear history
  /save <name>       Save session
  /load <name>       Load session
  /exit              Quit
"""


def cli_repl(config: Config, model: str, system_prompt: str) -> None:
    session = Session()
    model = OllamaClient.normalize(model)

    print(f"\n╭─ Ollama CLI Chat ─────────────────────╮")
    print(f"│ Model: {model:<31s} │")
    print(f"╰───────────────────────────────────────╯")
    print("Type /help for commands.\n")

    while True:
        try:
            text = input("you> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nbye")
            return

        if not text:
            continue

        if text.startswith("/"):
            parts = text.split(maxsplit=1)
            cmd, arg = parts[0].lower(), (parts[1].strip() if len(parts) > 1 else "")

            if cmd in ("/exit", "/quit"):
                print("bye"); return
            elif cmd == "/help":
                print(HELP)
            elif cmd == "/models":
                try:
                    for m in OllamaClient.list_models():
                        print(f"  - {m}")
                except Exception as e:
                    print(f"Error: {e}")
            elif cmd == "/model" and arg:
                model = arg; print(f"Model: {model}")
            elif cmd == "/pull" and arg:
                try:
                    OllamaClient.pull(arg, lambda s, p: print(f"\r  {s} ({p:.0%})", end=""))
                    print("\nDone!")
                except Exception as e:
                    print(f"Error: {e}")
            elif cmd == "/system" and arg:
                system_prompt = arg; print("System prompt updated.")
            elif cmd == "/clear":
                session.clear(); print("Cleared.")
            elif cmd == "/save" and arg:
                try:
                    print(f"Saved: {session.save(arg)}")
                except Exception as e:
                    print(f"Error: {e}")
            elif cmd == "/load" and arg:
                try:
                    session = Session.load(arg)
                    print(f"Loaded: {arg} ({len(session.history)} messages)")
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Unknown: {cmd}. Try /help")
            continue

        model = OllamaClient.normalize(model)
        if not OllamaClient.model_exists(model):
            print(f"⚠ Model '{model}' not found. Use /pull {model}")
            continue

        messages = session.build_messages(system_prompt, text)
        print(f"\nassistant[{model}]>")

        try:
            response = OllamaClient.stream_chat(
                model, messages,
                on_token=lambda t: (sys.stdout.write(t), sys.stdout.flush())
            )
            print("\n")
            session.add("user", text)
            session.add("assistant", response)
        except Exception as e:
            print(f"\n⚠ Error: {e}\n")


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

def main() -> int:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)

    parser = argparse.ArgumentParser(description="Ollama Chat Agent")
    parser.add_argument("--model", default=None, help="Model to use")
    parser.add_argument("--system", default=None, help="System prompt")
    parser.add_argument("--cli", action="store_true", help="Use CLI mode instead of GUI")
    parser.add_argument("--set-default-model", default=None, help="Save default model and exit")
    args = parser.parse_args()

    config = Config.load()

    if args.set_default_model:
        config.default_model = args.set_default_model
        config.save()
        print(f"Default model saved: {config.default_model}")
        return 0

    model = args.model or config.default_model
    system_prompt = args.system or config.system_prompt

    if args.cli:
        try:
            cli_repl(config, model, system_prompt)
        except KeyboardInterrupt:
            print("\nbye")
        return 0

    app = ChatGUI(config, model, system_prompt)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())