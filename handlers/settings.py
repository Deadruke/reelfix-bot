"""
Обработчик настроек бота
"""
import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import config

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("settings"))
async def settings_handler(message: Message):
    """
    Обработка команды /settings
    
    Args:
        message: Объект сообщения от пользователя
    """
    try:
        settings_text = """
⚙️ <b>Настройки REELFIX</b>

<b>Текущие настройки:</b>

• <b>BOT_TOKEN:</b> {'✅ задан' if config.BOT_TOKEN else '❌ не задан'}
• <b>OPENAI_API_KEY:</b> {'✅ задан' if config.OPENAI_API_KEY else '❌ не задан'}
• <b>FFmpeg:</b> {'✅ настроен' if config.FFMPEG_PATH else '❌ не настроен'}

<b>Настройки видео:</b>
• <b>Максимальный размер:</b> {config.MAX_VIDEO_SIZE_MB} MB
• <b>Максимальная длительность:</b> {config.MAX_VIDEO_DURATION_MIN} мин
• <b>Разрешение по умолчанию:</b> {config.DEFAULT_RESOLUTION}

<b>Настройки AI:</b>
• <b>Модель Whisper:</b> {config.model_size}
• <b>Качество:</b> {config.DEFAULT_FRAME_RATE} FPS

<b>Доступные команды:</b>
/settings - Показать настройки
/help - Справка
/video - Обработка видео
        """.format(
            **{
                "config": config,
                "BOT_TOKEN": config.BOT_TOKEN,
                "OPENAI_API_KEY": config.OPENAI_API_KEY,
                "FFmpeg": config.FFMPEG_PATH,
                "MAX_VIDEO_SIZE_MB": config.MAX_VIDEO_SIZE_MB,
                "MAX_VIDEO_DURATION_MIN": config.MAX_VIDEO_DURATION_MIN,
                "DEFAULT_RESOLUTION": config.DEFAULT_RESOLUTION,
                "model_size": "base"
            }
        )
        
        await message.answer(settings_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка в settings_handler: {e}")
        await message.answer("Произошла ошибка при отображении настроек.")


@router.callback_query(F.data.startswith("settings_"))
async def settings_callback(callback: CallbackQuery):
    """
    Обработка callback-запросов настроек
    
    Args:
        callback: Объект callback-запроса
    """
    try:
        data = callback.data
        
        if data == "settings_refresh":
            await settings_handler(callback.message)
            await callback.answer("✅ Настройки обновлены")
            
        else:
            await callback.answer("❌ Неизвестная настройка")
            
    except Exception as e:
        logger.error(f"Ошибка в settings_callback: {e}")
        await callback.answer("Произошла ошибка.")