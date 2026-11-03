# OpenAIPilot

OpenAIPilot is a Python prototype that lets you connect a language model (OpenAI API or a local Ollama server) to control a Windows PC.

## Features (MVP)
- **Model integration** – OpenAI Chat API **or** Ollama (local **or** Ollama Cloud) via a unified interface.
- **System control** – launch applications, simulate mouse/keyboard actions via `pyautogui`.
- **Process awareness** – checks if an app is already running using `psutil`.
- **Application discovery** – searches common installation folders (and optionally the whole C: drive) for an executable.
- **System tray** – small tray icon powered by `pystray` with an exit menu.
- **Hot‑keys** – configurable hot‑keys (default: `Ctrl+Alt+T` opens Telegram).
- **Logging** – rotating logs written to `logs/openai_pilot.log`.
- **Voice commands** – scaffold using `SpeechRecognition` (future).

## Project layout
```
OpenAIPilot/
├─ openaipilot/
│   ├─ __init__.py
│   ├─ main.py
│   ├─ config.py
│   ├─ logger.py
│   ├─ model/
│   │   ├─ __init__.py
│   │   ├─ base.py
│   │   ├─ openai_provider.py
│   │   └─ ollama_provider.py
│   ├─ controller/
│   │   └─ system_controller.py
│   ├─ tray/
│   │   └─ tray_icon.py
│   ├─ voice/
│   │   └─ recognizer.py
│   └─ utils/
│       └─ helpers.py   # (placeholder for future helpers)
├─ scripts/
│   ├─ install_deps.bat
│   └─ start.bat
├─ config.json          # user‑editable configuration (ignored by Git)
├─ requirements.txt
├─ .gitignore
├─ LICENSE
└─ README.md
```

## Quick start (Windows)
1. **Clone the repository** and open the folder in a terminal.
2. Run `scripts\install_deps.bat` – this creates a virtual environment and installs all dependencies.
3. Edit `config.json`:
   - Insert your OpenAI API key (`openai_api_key`).
   - Adjust hot‑keys or add other apps if you wish.
4. Run `scripts\start.bat` – the tray icon appears and the hot‑key `Ctrl+Alt+T` will open Telegram.

## Configuration (config.json)
```json
{
  "model_provider": "openai",          // "openai", "ollama", or "ollama_cloud"
  "openai_api_key": "YOUR_KEY_HERE",
  "ollama_api_key": "YOUR_OLLAMA_CLOUD_KEY",   // Required only if using "ollama_cloud"
  "ollama_url": "http://127.0.0.1:11434",       // Local Ollama server (used when provider is "ollama")
  "ollama_cloud_url": "https://api.ollama.com/v1", // Ollama Cloud endpoint (default)
  "ollama_model": "mistral",                    // Model name for Ollama (local or cloud)
  "openai_model": "gpt-3.5-turbo",              // Model name for OpenAI (optional)
  "log_level": "INFO",
  "app_search_paths": [
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\Users\\%USERNAME%\\AppData\\Local",
    "C:\\Users\\%USERNAME%\\AppData\\Roaming"
  ],
  "hotkeys": {
    "open_telegram": "ctrl+alt+t"
  }
}
```

- Set `model_provider` to `"ollama_cloud"` and fill in `ollama_api_key` to use the cloud service.
- For local usage keep `model_provider` as `"ollama"` and ensure `ollama_url` points to your local server.
```

## Adding more model providers
Implement a new class inheriting from `ModelProvider` in `openaipilot/model/` and register it in `main.py` based on the `model_provider` setting.

## Contributing
Feel free to open issues or pull requests. Future work includes:
- Voice‑command integration (using SpeechRecognition).
- A lightweight web UI (FastAPI).
- More robust application discovery (searching the Start menu index).
- Security sandboxing and user confirmation for arbitrary commands.

---
*This README is a starting point – keep it updated as the project evolves.*
