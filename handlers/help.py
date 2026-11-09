"""
Обработчик справки
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("help"))
async def help_handler(message: Message):
    """
    Обработка команды /help
    
    Args:
        message: Объект сообщения от пользователя
    """
    try:
        help_text = """
🎬 <b>REELFIX - Справка</b>

<b>Основные команды:</b>
/start - Главное меню
/help - Эта справка
/settings - Настройки бота
/video - Обработка видео

<b>Функции обработки видео:</b>

1. <b>Автоматические субтитры</b>
   • Whisper AI для точной транскрибации
   • Поддержка 50+ языков
   • 10+ стилей оформления

2. <b>Улучшение качества</b>
   • Upscaling до 4K
   • Удаление шума
   • Стабилизация
   • Улучшение резкости

3. <b>Обработка аудио</b>
   • Удаление шума
   • Нормализация громкости
   • Добавление музыки
   • Изменение формата

4. <b>Редактирование видео</b>
   • Обрезка по времени
   • Изменение формата
   • Изменение размера
   • Удаление пауз

5. <b>Цветокоррекция</b>
   • Яркость, контраст, насыщенность
   • Цветовые грейды
   • Фильтры

<b>Отправь видео, и я начну обработку!</b>
        """
        
        await message.answer(help_text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка в help_handler: {e}")
        await message.answer("Произошла ошибка при отображении справки.")