"""
System tray icon implementation using pystray.
"""

import threading
try:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw
except Exception as e:
    pystray = None
    item = None
    Image = None
    ImageDraw = None
    # logger will be imported below; we log after logger import
    # We'll set a flag to log once logger is available.
    _import_error = e

from ..logger import logger
if pystray is None:
    logger.warning(f"pystray (or Pillow) not available: {_import_error}")


def create_image():
    """Generate a simple 64x64 black‑white icon.
    The image is created on the fly so the repository does not need to ship an .ico file.
    """
    if Image is None:
        # No Pillow available – return None, start_tray will handle it.
        return None
    width = 64
    height = 64
    color1 = "black"
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    # Draw a white square in the centre for visual contrast
    dc.rectangle(
        [(width // 2 - 10, height // 2 - 10), (width // 2 + 10, height // 2 + 10)],
        fill="white"
    )
    return image


def on_exit(icon, item):
    logger.info("Exiting OpenAIPilot via tray menu.")
    icon.stop()


def start_tray():
    """Create and run the system tray icon in the main thread.
    This function blocks until the tray icon is stopped.
    """
    if pystray is None:
        logger.info("pystray not available – tray icon disabled.")
        return
    icon = pystray.Icon(
        "OpenAIPilot",
        create_image(),
        "OpenAIPilot",
        menu=pystray.Menu(
            item('Exit', on_exit)
        )
    )
    logger.info("Starting system tray icon.")
    icon.run()
