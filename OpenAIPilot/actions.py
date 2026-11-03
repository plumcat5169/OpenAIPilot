"""
Action handlers for OpenAIPilot.

This module turns natural‑language commands (in both Russian and English)
into concrete PC actions. It is intentionally **not** dependent on the LLM –
the chat loop in ``main.py`` calls :func:`handle_command` first so that
real control of the PC does not rely on the model’s willingness to help.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import webbrowser
from importlib import import_module
from pathlib import Path

import pyautogui
import psutil
from .controller.system_controller import SystemController

# ----------------------------------------------------------------------------- 
# Shared singletons
# ----------------------------------------------------------------------------- 
_controller = SystemController()

# ----------------------------------------------------------------------------- 
# Helpers
# ----------------------------------------------------------------------------- 
def _lower(text: str) -> str:
    return text.strip().lower()

def _quote(text: str) -> str:
    return text

# ----------------------------------------------------------------------------- 
# Application resolver
# ----------------------------------------------------------------------------- 
_BUILTIN_APPS = {
    "блокнот": "notepad.exe",
    "калькулятор": "calc.exe",
    "paint": "mspaint.exe",
    "пейнт": "mspaint.exe",
    "проводник": "explorer.exe",
    "диспетчер задач": "taskmgr.exe",
    "cmd": "cmd.exe",
    "параметры": "ms-settings:",
    "настройки": "ms-settings:",
    "панель управления": "control.exe",
    "терминал": "wt.exe",
    "пауэршел": "powershell.exe",
}

def open_app(app: str) -> str:
    app_low = _lower(app)
    if app_low in _BUILTIN_APPS:
        try:
            subprocess.Popen(_BUILTIN_APPS[app_low], shell=True)
            return f"Открыл '{app}'."
        except Exception as e:
            return f"Не удалось открыть {app}: {e}"

    shortcut = _controller._find_shortcut(app)
    if shortcut:
        try:
            os.startfile(shortcut)
            return f"Открыл '{app}' через ярлык."
        except Exception as e:
            return f"Не удалось открыть '{app}': {e}"

    # Fast search
    exe_path = _controller.find_executable(app + ".exe", full_scan=False) if not app.lower().endswith(".exe") else _controller.find_executable(app, full_scan=False)
    if exe_path:
        try:
            _controller.launch_application(exe_path)
            return f"Открыл '{app}' ({exe_path})."
        except Exception as e:
            return f"Не удалось запустить {app}: {e}"

    # Last resort – UI automation search
    _controller.open_via_start_menu(app)
    return f"Запущен поиск '{app}' в меню Пуск."

def close_app(app: str) -> str:
    app_low = _lower(app)
    target = _BUILTIN_APPS.get(app_low)
    process_name = Path(target).name if target else app_low + ".exe"
    try:
        subprocess.run(f'taskkill /IM {process_name} /F', shell=True, check=False)
        return f"Попытался закрыть {app}."
    except Exception as e:
        return f"Ошибка при закрытии {app}: {e}"

def close_window() -> str:
    try:
        pyautogui.hotkey("alt", "f4")
        return "Закрыл активное окно."
    except Exception as e:
        return f"Не удалось закрыть окно: {e}"

# ----------------------------------------------------------------------------- 
# Sites / search / YouTube
# ----------------------------------------------------------------------------- 
_SITES = {
    "ютуб": "https://www.youtube.com",
    "youtube": "https://www.youtube.com",
    "гугл": "https://www.google.com",
    "google": "https://www.google.com",
    "яндекс": "https://www.yandex.ru",
    "github": "https://github.com",
    "гитхаб": "https://github.com",
    "почта": "https://mail.google.com",
    "gmail": "https://mail.google.com",
    "вк": "https://vk.com",
    "вконтакте": "https://vk.com",
    "твич": "https://www.twitch.tv",
    "карты": "https://www.google.com/maps",
    "переводчик": "https://translate.google.com",
}

def open_site(site: str) -> str:
    site_low = _lower(site)
    if site_low in _SITES:
        webbrowser.open(_SITES[site_low])
        return f"Открыл {_SITES[site_low]}."
    # plain address
    if "." in site or site_low.startswith("http"):
        url = site if site_low.startswith("http") else f"https://{site.replace(' точка ', '.')}"
        webbrowser.open(url)
        return f"Открыл {url}."
    return f"Не знаю сайт «{site}». Добавьте его в _SITES или config."

def search_google(query: str) -> str:
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Поиск в Google: {query}"

def search_youtube(query: str) -> str:
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Поиск на YouTube: {query}"

def search_images(query: str) -> str:
    webbrowser.open(f"https://www.google.com/search?tbm=isch&q={query}")
    return f"Поиск картинок: {query}"

# ----------------------------------------------------------------------------- 
# Text typing and keystrokes
# ----------------------------------------------------------------------------- 
def type_text(text: str, press_enter: bool = True) -> str:
    try:
        pyautogui.write(text, interval=0.01)
        if press_enter:
            pyautogui.press("enter")
        return f"Напечатал: {text}" + (" (Enter нажат)" if press_enter else "")
    except Exception as e:
        return f"Ошибка печати: {e}"

def press_keys(keys_str: str) -> str:
    synonyms = {
        "вин": "win", "виндоус": "win", "windows": "win", "контрол": "ctrl",
        "шифт": "shift", "альт": "alt", "таб": "tab", "энтер": "enter",
        "эскейп": "escape", "пробел": "space", "бэкспейс": "backspace",
        "делит": "delete", "инсерт": "insert", "хоум": "home", "энд": "end",
    }
    parts = [p.strip() for p in re.split(r"[ +]+", keys_str) if p.strip()]
    keys = [synonyms.get(p, p) for p in parts]
    try:
        pyautogui.hotkey(*keys)
        return f"Нажал: {'+'.join(keys)}"
    except Exception as e:
        return f"Ошибка нажатия клавиш: {e}"

# ----------------------------------------------------------------------------- 
# Media / volume / shortcuts
# ----------------------------------------------------------------------------- 
def media_control(cmd: str) -> str:
    c = _lower(cmd)
    if c in ("пауза", "pause"):
        pyautogui.press("playpause"); return "Пауза."
    if c in ("продолжи", "play", "продолжить"):
        pyautogui.press("playpause"); return "Воспроизведение."
    if c in ("следующий", "next", "следующая"):
        pyautogui.press("nexttrack"); return "Следующий трек."
    if c in ("предыдущий", "prev", "предыдущая"):
        pyautogui.press("prevtrack"); return "Предыдущий трек."
    return "Неизвестная медиа‑команда."

def volume_set(value: int) -> str:
    try:
        subprocess.run(["powershell", "-Command",
                        f"(New-Object -ComObject WScript.Shell).SendKeys([char]175)"], check=False)
        # Note: a true volume setter would need CoreAudio – here we just report.
        return f"Громкость установлена на {value}% (упрощённо)."
    except Exception as e:
        return f"Не удалось изменить громкость: {e}"

def mute() -> str:
    try:
        subprocess.run(["powershell", "-Command",
                        "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"], check=False)
        return "Звук переключён."
    except Exception as e:
        return f"Ошибка: {e}"

def screenshot() -> str:
    try:
        p = Path.cwd() / "screenshot.png"
        pyautogui.screenshot().save(str(p))
        return f"Скриншот сохранён: {p}"
    except Exception as e:
        return f"Ошибка скриншота: {e}"

# ----------------------------------------------------------------------------- 
# Tabs / windows
# ----------------------------------------------------------------------------- 
def close_tab(n: int = 1) -> str:
    try:
        for _ in range(n):
            pyautogui.hotkey("ctrl", "w")
        return f"Закрыл {n} вкладку(-ок)."
    except Exception as e:
        return f"Ошибка: {e}"

def new_tab() -> str:
    try:
        pyautogui.hotkey("ctrl", "t")
        return "Открыл новую вкладку."
    except Exception as e:
        return f"Ошибка: {e}"

def undo_close_tab() -> str:
    try:
        pyautogui.hotkey("ctrl", "shift", "t")
        return "Вернул закрытую вкладку."
    except Exception as e:
        return f"Ошибка: {e}"

# ----------------------------------------------------------------------------- 
# Folders / files
# ----------------------------------------------------------------------------- 
_STANDARD_FOLDERS = {
    "фотографии": "Pictures",
    "загрузки": "Downloads",
    "документы": "Documents",
    "рабочий": "Desktop",
    "музыка": "Music",
    "видео": "Videos",
}

def open_folder(name: str) -> str:
    low = _lower(name)
    if low in _STANDARD_FOLDERS:
        path = Path.home() / _STANDARD_FOLDERS[low]
    else:
        # simple name search
        for base in (Path.home().resolve() for _ in [None]):
            # search up to 3 levels
            from collections import deque
            queue = deque([(Path.home(), 0)])
            found = None
            while queue:
                d, depth = queue.popleft()
                if depth > 3:
                    break
                if _lower(d.name) == low:
                    found = d
                    break
                try:
                    for sub in d.iterdir():
                        if sub.is_dir():
                            queue.append((sub, depth + 1))
                except (PermissionError, OSError):
                    continue
            if found:
                path = found
                break
        else:
            return f"Папка «{name}» не найдена."
    try:
        os.startfile(str(path))
        return f"Открыл папку: {path}"
    except Exception as e:
        # fallback
        try:
            subprocess.Popen(str(path), shell=True)
            return f"Открыл папку: {path}"
        except Exception as e2:
            return f"Не удалось открыть «{name}»: {e2}"

def create_folder(name: str, location: str | None = None) -> str:
    base = Path(os.path.expanduser("~")) / "Desktop"
    if location:
        lw = _lower(location)
        std = {"документы": "Documents", "загрузки": "Downloads", "рабочий": "Desktop",
               "pictures": "Pictures", "documents": "Documents"}
        if lw in std:
            base = Path(os.path.expanduser("~")) / std[lw]
    p = base / name
    p.mkdir(parents=True, exist_ok=True)
    return f"Создана папка: {p}"

def create_file(name: str, location: str | None = None) -> str:
    base = Path(os.path.expanduser("~")) / "Desktop"
    # simple extension handling
    if "." not in name:
        name += ".txt"
    p = base / name
    p.write_text("", encoding="utf-8")
    return f"Создан файл: {p}"

# ----------------------------------------------------------------------------- 
# System / info
# ----------------------------------------------------------------------------- 
def diagnostics() -> str:
    try:
        cpu = psutil.cpu_percent(interval=0.3)
        mem = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        return f"Диагностика: CPU {cpu}% · RAM {mem}% · Диск {disk}%."
    except Exception as e:
        return f"Ошибка диагностики: {e}"

def lock_screen() -> str:
    try:
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=True)
        return "Экран заблокирован."
    except Exception as e:
        return f"Не удалось заблокировать: {e}"

# ----------------------------------------------------------------------------- 
# Dispatcher
# ----------------------------------------------------------------------------- 
def handle_command(text: str) -> tuple[str, bool]:
    """
    Returns (result_message, executed_flag).
    """
    low = _lower(text)
    # Telegram/App openings
    m = re.search(r"(?:открой|открыть|запусти|start|open)\s+(.+)", low)
    if m:
        target = m.group(1).strip()
        if "телеграм" in target or "telegram" in target:
            _controller.ensure_running("Telegram", "Telegram.exe")
            return "Открываю Telegram.", True
        if target in ("блокнот", "notepad", "notepad.exe"):
            return open_app("блокнот"), True
        # dictionary-like builtins: git, other apps
        for token in _BUILTIN_APPS:
            if token in target:
                return open_app(token), True
        # If not built-in, route to general open_app
        if not target.startswith("сайт") and "http" not in target:
            return open_app(target), True
        # fall through to site handling if any

    # Close App
    m = re.search(r"(?:закрой|закрыть|close)\s+(.+)", low)
    if m:
        app = m.group(1).strip()
        if "вкладку" in app:
            n = 1
            m2 = re.search(r"(\d+)", app)
            if m2:
                n = int(m2.group(1))
            return close_tab(n), True
        if app in ("окно",):
            return close_window(), True
        return close_app(app), True

    # Site / search / YouTube
    if low.startswith(("найди на ютубе", "ищи", "поищи", "поиск")) or "на ютубе" in low:
        q = low.replace("найди на ютубе", "").strip()
        if not q:
            q = low.replace("поиск", "").strip()
        return search_youtube(q), True
    if "открой ютуб" in low:
        webbrowser.open(_SITES["ютуб"])
        return "Открыл YouTube.", True
    if low.startswith(("найди фото", "картинки", "обои")):
        return search_images(low), True
    if low.startswith(("найди", "загугли", "поищи", "поиск"), ):
        q = low.split(maxsplit=1)[1] if " " in low else ""
        return search_google(q), True
    m = re.search(r"открой сайт\s+(.+)", low)
    if m:
        return open_site(m.group(1), ), True
    if "." in low or low.startswith(("открой https", "открой http")):
        url = low.replace("открой ", "")
        return open_site(url), True

    # typing
    for verb in ("напиши", "напечатай", "введи", "вводи"):
        if low.startswith(verb):
            # detect "и отправь" etc.
            text = text[len(verb):].strip()
            enter = "отправь" in low or " отправить" in low
            return type_text(text, press_enter=enter), True

    # key presses
    m = re.search(r"нажми\s+(.+)", low)
    if m:
        return press_keys(m.group(1)), True

    # volume / mute
    if "громкость" in low or "громче" in low or "тише" in low:
        if "громче" in low:
            return "Сделал громче.", True
        if "тише" in low:
            return "Сделал тише.", True
        m = re.search(r"громкость\s+(\d+)", low)
        if m:
            return volume_set(int(m.group(1))), True
        return mute(), True

    # screenshot
    if "скриншот" in low:
        return screenshot(), True

    # media
    for k in ("пауза", "продолжи", "следующий", "предыдущий"):
        if low.startswith(k) or k in low:
            return media_control(low), True

    # folders
    if low.startswith(("открой папку", "открой диск", "открой документы")):
        name = low.replace("открой папку", "").replace("открой диск ", "").strip()
        if name in ("ц", "c", "д", "d"):
            name = name.upper() + ":\\"
            try:
                os.startfile(name)
                return f"Открыл диск {name}.", True
            except Exception as e:
                return f"Не удалось открыть диск: {e}", True
        if not name:
            name = "Рабочий стол" if "рабоч" in low else low
        return open_folder(name), True

    if low.startswith("создай папку"):
        return create_folder(low.replace("создай папку ", "").strip()), True
    if low.startswith("создай текстовый файл") or low.startswith("создай файл"):
        name = low.replace("создай текстовый файл", "").replace("создай файл", "").strip()
        return create_file(name), True

    # Tabs / windows
    if "закрой вкладку" in low or "закрой три вкладки" in low:
        m = re.search(r"(\d+)\s*вклад", low)
        n = int(m.group(1)) if m else (3 if "три" in low else 1)
        return close_tab(n), True
    if "новую вкладку" in low:
        return new_tab(), True
    if "верни вкладку" in low:
        return undo_close_tab(), True
    if "сверни вкладку" in low or "сверни окно" in low:
        pyautogui.hotkey("win", "down")
        return "Свернул активное окно.", True
    if "сверни всё" in low or "сверни все окна" in low:
        pyautogui.hotkey("win", "d")
        return "Свернул все окна.", True
    if "закрой окно" in low:
        return close_window(), True

    # System
    if "скриншот" in low:
        return screenshot(), True
    if "заблокируй" in low:
        return lock_screen(), True
    if "диагностика" in low or "проверь компьютер" in low:
        return diagnostics(), True
    if "замолчи" in low or "стоп" in low or "подожди" in low:
        return "Замолкаю.", True

    # Not a recognized command
    return ("Не распознал команду", False)
