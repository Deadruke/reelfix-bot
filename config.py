"""
Конфигурация REELFIX бота
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Telegram
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
    
    # AI Services
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
    STABILITY_API_KEY = os.getenv("STABILITY_API_KEY", "")
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")
    
    # FFmpeg
    FFMPEG_PATH = os.getenv("FFMPEG_PATH", "/usr/bin/ffmpeg")
    
    # Video settings
    MAX_VIDEO_SIZE_MB = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))
    MAX_VIDEO_DURATION_MIN = int(os.getenv("MAX_VIDEO_DURATION_MIN", "10"))
    DEFAULT_RESOLUTION = os.getenv("DEFAULT_RESOLUTION", "1080p")
    DEFAULT_FRAME_RATE = int(os.getenv("DEFAULT_FRAME_RATE", "30"))
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./reelfix.db")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls):
        """Проверка обязательных переменных"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не задан!")
        if not cls.OPENAI_API_KEY:
            print("Внимание: OPENAI_API_KEY не задан, Whisper может работать медленнее")
        return True

config = Config()