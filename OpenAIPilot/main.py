"""
Entry point for the OpenAIPilot application.
Initialises configuration, logging, model provider, system controller, hot‑keys and the tray icon.
"""

import threading
import time
import sys
from .controller.system_controller import SystemController
from .tray.tray_icon import start_tray
from .logger import logger
try:
    import keyboard
except Exception as e:
    keyboard = None
    logger.warning(f"keyboard module not available: {e}")

# Import the model provider based on configuration lazily inside main()
from .config import load_config
from .actions import handle_command


def get_model_provider():
    cfg = load_config()
    provider_name = cfg.get("model_provider", "openai").lower()
    if provider_name == "openai":
        from .model.openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif provider_name == "ollama":
        from .model.ollama_provider import OllamaProvider
        return OllamaProvider()
    elif provider_name in ("ollama_cloud", "ollama-cloud"):  # Ollama Cloud API
        from .model.ollama_cloud_provider import OllamaCloudProvider
        return OllamaCloudProvider()
    else:
        raise ValueError(f"Unsupported model provider: {provider_name}")


def main():
    logger.info("Starting OpenAIPilot...")
    cfg = load_config()
    controller = SystemController()

    # ---------------------------------------------------------------------
    # Hot‑key handling – load from config, default is Ctrl+Alt+T for Telegram
    # ---------------------------------------------------------------------
    hotkeys = cfg.get("hotkeys", {})
    telegram_hotkey = hotkeys.get("open_telegram", "ctrl+alt+t")

    def open_telegram():
        logger.info("Hot‑key triggered – opening Telegram")
        # Telegram executable name is typically "Telegram.exe" on Windows.
        controller.ensure_running(app_name="Telegram", exe_name="Telegram.exe")

    if keyboard:
        keyboard.add_hotkey(telegram_hotkey, open_telegram)
        logger.info(f"Registered hot‑key '{telegram_hotkey}' for opening Telegram.")
    else:
        logger.warning("keyboard module not available – hot‑keys disabled.")

    # ---------------------------------------------------------------------
    # System tray – run in a background daemon thread so the main thread can stay
    # responsive to hot‑keys and future voice commands.
    # ---------------------------------------------------------------------
    tray_thread = threading.Thread(target=start_tray, daemon=True)
    tray_thread.start()

    # ---------------------------------------------------------------------
    # Model provider – instantiate (used later for voice/LLM integration).
    # ---------------------------------------------------------------------
    try:
        model = get_model_provider()
        logger.info(f"Model provider '{cfg.get('model_provider')}' initialized.")
    except Exception as e:
        logger.error(f"Failed to initialise model provider: {e}")
        model = None

    # ---------------------------------------------------------------------
    # Simple CLI chat loop – send user messages to the model and act on
    # recognised commands (e.g., "open telegram").
    # ---------------------------------------------------------------------
    def handle_response(resp: str):
        """Parse model response for simple commands and execute them.
        Currently supports opening Telegram by detecting the phrase
        "open telegram" (case‑insensitive). Extend this function for more
        commands as needed.
        """
        lower = resp.lower()
        # Try the structured COMMAND: line first
        for line in resp.splitlines():
            stripped = line.strip()
            if stripped.lower().startswith("command:"):
                cmd = stripped[len("command:"):].strip().lower()
                if "open telegram" in cmd:
                    logger.info("Model requested to open Telegram – invoking controller.")
                    controller.ensure_running(app_name="Telegram", exe_name="Telegram.exe")
                    return
                # Add more mappings here
        # Fallback: simple keyword detection
        if "open telegram" in lower:
            logger.info("Detected 'open telegram' in response – invoking controller.")
            controller.ensure_running(app_name="Telegram", exe_name="Telegram.exe")

    if model:
        logger.info("Entering simple CLI chat – type 'exit' or Ctrl+C to quit.")
        try:
            while True:
                user_input = input("You: ")
                if user_input.strip().lower() in ("exit", "quit"):
                    break
                try:
                    result, executed = handle_command(user_input)
                except Exception as e:
                    logger.error(f"Error in handle_command: {e}")
                    result, executed = "", False
                if executed:
                    if result:
                        print(f"System: {result}")
                    continue
                try:
                    resp = model.generate(user_input)
                except Exception as e:
                    logger.error(f"Error during model generate: {e}")
                    resp = ""
                print(f"Model: {resp}")
        except (KeyboardInterrupt, EOFError):
            logger.info("Chat loop interrupted by user/EoF.")
    else:
        logger.warning("Model provider not available – chat interface disabled.")

    # ---------------------------------------------------------------------
    # Keep the process alive while tray and hot‑keys work.
    # ---------------------------------------------------------------------
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received – shutting down OpenAIPilot.")
    finally:
        # Cleanup
        if model:
            try:
                model.close()
            except Exception as e:
                logger.warning(f"Error closing model provider: {e}")
        if keyboard:
            keyboard.unhook_all()
        logger.info("Good‑bye!")
        # Allow a brief moment for the tray thread to exit gracefully
        time.sleep(0.5)
        sys.exit(0)


if __name__ == "__main__":
    main()
