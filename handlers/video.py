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


VIDEO_EXTENSIONS = (".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v", ".3gp")


async def _save_video_and_ask_action(message: Message, state: FSMContext, file_id: str, filename: str = "video.mp4"):
    """Общая логика: скачать видео, сохранить путь в FSM и попросить выбрать действие."""
    logger.info(f"Получено видео от {message.from_user.id if message.from_user else '?'}: file_id={file_id}")

    if not config.BOT_TOKEN:
        await message.answer("⚠️ <b>BOT_TOKEN не задан!</b>\n\nПожалуйста, добавьте BOT_TOKEN в переменные окружения.")
        return

    await state.set_state(VideoStates.waiting_for_video)

    os.makedirs("temp", exist_ok=True)
    # Безопасное имя файла: только message_id + расширение из исходного имени
    ext = os.path.splitext(filename)[1].lower()
    if ext not in VIDEO_EXTENSIONS:
        ext = ".mp4"
    file_path = f"temp/{message.message_id}{ext}"

    await message.answer("⏳ Скачиваю видео...")

    try:
        # Скачиваем через Bot API. file.download() в aiogram 3.4.1 принимает путь строкой.
        file_obj = await message.bot.get_file(file_id)
        await file_obj.download(destination=file_path)
    except Exception as e:
        logger.error(f"Ошибка скачивания видео file_id={file_id}: {e}")
        await message.answer("❌ Не удалось скачать видео. Попробуй отправить его ещё раз, желательно файлом (без сжатия).")
        return

    if not os.path.exists(file_path):
        logger.error(f"Файл не создался после скачивания: {file_path}")
        await message.answer("❌ Видео не сохранилось. Попробуй отправить ещё раз.")
        return

    # Сохраняем путь, чтобы следующий шаг обработки знал, какой файл брать
    await state.update_data(video_path=file_path)

    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    logger.info(f"Видео сохранено: {file_path} ({size_mb:.2f} MB)")

    await message.answer(
        f"✅ Видео загружено!\n\n"
        f"Размер: {size_mb:.2f} MB\n"
        f"Отправьте номер действия:\n"
        f"• <b>1</b> - Автоматические субтитры\n"
        f"• <b>2</b> - Улучшение качества\n"
        f"• <b>3</b> - Обработка аудио\n"
        f"• <b>4</b> - Обрезка и формат\n"
        f"• <b>5</b> - Цветокоррекция\n"
        f"• <b>6</b> - Добавить музыку"
    )


@router.message(Command("video"))
async def video_handler(message: Message, state: FSMContext):
    """
    Обработка команды /video
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
async def handle_photo_upload(message: Message, state: FSMContext):
    """
    Обработка загрузки фото (иногда видео в Telegram приходит как фото).
    Раньше эта функция называлась handle_video_upload и перезаписывала
    хендлер для F.video — из-за этого один из них мог не работать.
    """
    try:
        if not message.photo:
            return
        photo = message.photo[-1]
        await _save_video_and_ask_action(message, state, photo.file_id, "video.mp4")
    except Exception as e:
        logger.error(f"Ошибка при обработке фото: {e}")
        await message.answer("Произошла ошибка при загрузке видео. Попробуйте позже.")


@router.message(F.video)
async def handle_video_upload(message: Message, state: FSMContext):
    """
    Обработка загрузки видео (прямо видео)
    """
    try:
        if not message.video:
            return
        await _save_video_and_ask_action(message, state, message.video.file_id, message.video.file_name or "video.mp4")
    except Exception as e:
        logger.error(f"Ошибка при обработке видео: {e}")
        await message.answer("Произошла ошибка при загрузке видео. Попробуйте позже.")


@router.message(F.animation)
async def handle_animation_upload(message: Message, state: FSMContext):
    """
    Обработка GIF/анимации — Telegram присылает их как animation, а не video.
    """
    try:
        if not message.animation:
            return
        await _save_video_and_ask_action(message, state, message.animation.file_id, message.animation.file_name or "video.mp4")
    except Exception as e:
        logger.error(f"Ошибка при обработке анимации: {e}")
        await message.answer("Произошла ошибка при загрузке видео. Попробуйте позже.")


@router.message(F.video_note)
async def handle_video_note_upload(message: Message, state: FSMContext):
    """
    Обработка кружочка (video_note).
    """
    try:
        if not message.video_note:
            return
        await _save_video_and_ask_action(message, state, message.video_note.file_id, "video.mp4")
    except Exception as e:
        logger.error(f"Ошибка при обработке кружочка: {e}")
        await message.answer("Произошла ошибка при загрузке видео. Попробуйте позже.")


@router.message(F.document)
async def handle_document_upload(message: Message, state: FSMContext):
    """
    Обработка видео, отправленного файлом/документом.
    Это самый частый случай: большие видео и Reels часто приходят
    именно как document, а не как video — раньше они вообще не обрабатывались.
    """
    try:
        doc = message.document
        if not doc:
            return

        mime = (doc.mime_type or "").lower()
        filename = (doc.file_name or "").lower()

        is_video = mime.startswith("video/") or filename.endswith(VIDEO_EXTENSIONS)
        if not is_video:
            await message.answer("📎 Это не видео. Отправь, пожалуйста, видео — можно файлом, без сжатия.")
            return

        await _save_video_and_ask_action(message, state, doc.file_id, doc.file_name or "video.mp4")
    except Exception as e:
        logger.error(f"Ошибка при обработке документа: {e}")
        await message.answer("Произошла ошибка при загрузке видео. Попробуйте позже.")


@router.message(F.text)
async def handle_action_selection(message: Message, state: FSMContext):
    """
    Обработка выбора действия по цифре 1-6.
    ВАЖНО: фильтр F.text обязателен. Раньше здесь был @router.message()
    без фильтра, поэтому этот хендлер перехватывал ЛЮБОЕ сообщение,
    включая видео/документы, которые не подошли под предыдущие фильтры,
    и отвечал "Неизвестная команда" вместо обработки видео.
    """
    try:
        if not config.BOT_TOKEN:
            await message.answer("⚠️ <b>BOT_TOKEN не задан!</b>\n\nПожалуйста, добавьте BOT_TOKEN в переменные окружения.")
            return

        action = (message.text or "").strip()
        
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
            # Не спамим "Неизвестная команда" на каждый чих — только подсказываем
            current_state = await state.get_state()
            if current_state is not None:
                await message.answer("Неизвестная команда. Отправь цифру от 1 до 6 или отправь видео.")
            else:
                await message.answer("Отправь мне видео, и я помогу его обработать! 🎬")
            
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
