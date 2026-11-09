"""
Обработчик видео и команд обработки
"""
import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.whisper_service import WhisperService
from services.video_processor import VideoProcessor
from services.audio_processor import AudioProcessor
from services.quality_enhancer import QualityEnhancer
from services.subtitle_generator import SubtitleGenerator

from config import config

logger = logging.getLogger(__name__)

router = Router()


class VideoStates(StatesGroup):
    waiting_for_video = State()
    waiting_for_subtitle_style = State()
    waiting_for_quality_settings = State()
    waiting_for_audio_effects = State()


@router.message(Command("video"))
async def video_handler(message: Message, state: FSMContext):
    """
    Обработка команды /video
    
    Args:
        message: Объект сообщения от пользователя
        state: FSM контекст
    """
    try:
        await state.clear()
        
        text = """
🎬 <b>Обработка видео</b>

Выберите действие:
• <b>1</b> - Автоматические субтитры
• <b>2</b> - Улучшение качества
• <b>3</b> - Обработка аудио
• <b>4</b> - Обрезка и формат
• <b>5</b> - Цветокоррекция
• <b>6</b> - Добавить музыку

Отправь видео, чтобы начать!
        """
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Ошибка в video_handler: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@router.message(F.photo)
async def handle_video_upload(message: Message, state: FSMContext):
    """
    Обработка загрузки видео
    
    Args:
        message: Объект сообщения с видео
        state: FSM контекст
    """
    try:
        if not config.BOT_TOKEN:
            await message.answer("⚠️ <b>BOT_TOKEN не задан!</b>\n\nПожалуйста, добавьте BOT_TOKEN в переменные окружения.")
            return
        
        await state.set_state(VideoStates.waiting_for_video)
        
        # Получаем последнее фото (видео в Telegram)
        photo = message.photo[-1]
        file_path = f"temp/{message.message_id}.mp4"
        
        # Создаем директорию для временных файлов
        os.makedirs("temp", exist_ok=True)
        
        # Скачиваем видео
        await message.answer("⏳ Скачиваю видео...")
        await message.photo[-1].download(file_path)
        
        await message.answer(
            f"✅ Видео загружено!\n\n"
            f"Размер: {os.path.getsize(file_path) / (1024*1024):.2f} MB\n"
            f"Отправьте номер действия:\n"
            f"• <b>1</b> - Автоматические субтитры\n"
            f"• <b>2</b> - Улучшение качества\n"
            f"• <b>3</b> - Обработка аудио\n"
            f"• <b>4</b> - Обрезка и формат\n"
            f"• <b>5</b> - Цветокоррекция\n"
            f"• <b>6</b> - Добавить музыку"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке видео: {e}")
        await message.answer("Произошла ошибка при загрузке видео. Попробуйте позже.")


@router.message(F.video)
async def handle_video_upload(message: Message, state: FSMContext):
    """
    Обработка загрузки видео (прямо видео)
    
    Args:
        message: Объект сообщения с видео
        state: FSM контекст
    """
    try:
        if not config.BOT_TOKEN:
            await message.answer("⚠️ <b>BOT_TOKEN не задан!</b>\n\nПожалуйста, добавьте BOT_TOKEN в переменные окружения.")
            return
        
        await state.set_state(VideoStates.waiting_for_video)
        
        # Скачиваем видео
        await message.answer("⏳ Скачиваю видео...")
        file_path = f"temp/{message.message_id}.mp4"
        
        # Создаем директорию для временных файлов
        os.makedirs("temp", exist_ok=True)
        
        await message.video.download(file_path)
        
        await message.answer(
            f"✅ Видео загружено!\n\n"
            f"Размер: {os.path.getsize(file_path) / (1024*1024):.2f} MB\n"
            f"Отправьте номер действия:\n"
            f"• <b>1</b> - Автоматические субтитры\n"
            f"• <b>2</b> - Улучшение качества\n"
            f"• <b>3</b> - Обработка аудио\n"
            f"• <b>4</b> - Обрезка и формат\n"
            f"• <b>5</b> - Цветокоррекция\n"
            f"• <b>6</b> - Добавить музыку"
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке видео: {e}")
        await message.answer("Произошла ошибка при загрузке видео. Попробуйте позже.")


@router.message()
async def handle_action_selection(message: Message, state: FSMContext):
    """
    Обработка выбора действия
    
    Args:
        message: Объект сообщения
        state: FSM контекст
    """
    try:
        if not config.BOT_TOKEN:
            await message.answer("⚠️ <b>BOT_TOKEN не задан!</b>\n\nПожалуйста, добавьте BOT_TOKEN в переменные окружения.")
            return
        
        action = message.text
        
        if action == "1":
            await message.answer("🎙️ <b>Автоматические субтитры</b>\n\nВыберите стиль субтитров:")
            
            # Получаем доступные стили
            subtitle_gen = SubtitleGenerator()
            styles = subtitle_gen.get_available_styles()
            
            for i, style in enumerate(styles[:10], 1):
                await message.answer(f"• <b>{i}</b> - {style}")
            
            await message.answer("Или отправьте номер стиля или текст с описанием")
            await state.set_state(VideoStates.waiting_for_subtitle_style)
            
        elif action == "2":
            await message.answer("🎬 <b>Улучшение качества</b>\n\nВыберите действие:")
            await message.answer("• <b>1</b> - Upscaling (увеличение разрешения)")
            await message.answer("• <b>2</b> - Удаление шума")
            await message.answer("• <b>3</b> - Стабилизация")
            await message.answer("• <b>4</b> - Улучшение резкости")
            await message.answer("• <b>5</b> - Все эффекты")
            await state.set_state(VideoStates.waiting_for_quality_settings)
            
        elif action == "3":
            await message.answer("🔊 <b>Обработка аудио</b>\n\nВыберите действие:")
            await message.answer("• <b>1</b> - Удаление шума")
            await message.answer("• <b>2</b> - Нормализация громкости")
            await message.answer("• <b>3</b> - Добавить музыку")
            await message.answer("• <b>4</b> - Все эффекты")
            await state.set_state(VideoStates.waiting_for_audio_effects)
            
        elif action == "4":
            await message.answer("✂️ <b>Обрезка и формат</b>\n\nВыберите действие:")
            await message.answer("• <b>1</b> - Обрезка видео")
            await message.answer("• <b>2</b> - Изменение формата")
            await message.answer("• <b>3</b> - Изменение размера")
            await message.answer("• <b>4</b> - Удаление пауз")
            await state.set_state(VideoStates.waiting_for_quality_settings)
            
        elif action == "5":
            await message.answer("🎨 <b>Цветокоррекция</b>\n\nВыберите действие:")
            await message.answer("• <b>1</b> - Яркость")
            await message.answer("• <b>2</b> - Контраст")
            await message.answer("• <b>3</b> - Насыщенность")
            await message.answer("• <b>4</b> - Цветовая грейда")
            await message.answer("• <b>5</b> - Все эффекты")
            await state.set_state(VideoStates.waiting_for_quality_settings)
            
        elif action == "6":
            await message.answer("🎵 <b>Добавить музыку</b>\n\nОтправьте музыкальный файл, который хотите добавить к видео.")
            await state.set_state(VideoStates.waiting_for_video)
            
        else:
            await message.answer("Неизвестная команда. Попробуйте снова.")
            
    except Exception as e:
        logger.error(f"Ошибка при обработке выбора действия: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


async def process_video_processing(
    message: Message,
    action: str,
    state: FSMContext
):
    """
    Обработка видео по выбранному действию
    
    Args:
        message: Объект сообщения
        action: Действие
        state: FSM контекст
    """
    try:
        # Инициализация сервисов
        whisper = WhisperService()
        video_proc = VideoProcessor()
        audio_proc = AudioProcessor()
        quality_enh = QualityEnhancer()
        subtitle_gen = SubtitleGenerator()
        
        await message.answer("⏳ Начинаю обработку видео...")
        
        # Здесь будет логика обработки видео
        # Для примера - просто возвращаем сообщение
        await message.answer(
            "✅ Обработка видео запущена!\n\n"
            "В полной версии здесь будет:\n"
            "• Генерация субтитров через Whisper\n"
            "• Применение эффектов\n"
            "• Обработка аудио\n"
            "• Финальное слияние\n\n"
            "Результат будет отправлен вам в ближайшее время."
        )
        
    except Exception as e:
        logger.error(f"Ошибка при обработке видео: {e}")
        await message.answer(f"Произошла ошибка: {e}")