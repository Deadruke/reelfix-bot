"""
Обработчики команд и сообщений бота
"""
from .start import start_handler
from .video import video_handler
from .settings import settings_handler
from .help import help_handler

__all__ = [
    "start_handler",
    "video_handler",
    "settings_handler",
    "help_handler"
]