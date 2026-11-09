"""
REELFIX - Telegram Bot для обработки видео
Автор: Gubka-GPT
"""
import logging
import asyncio
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from config import config
from handlers import start, video, settings, help as help_handler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Инициализация диспетчера
dp = Dispatcher()


# Регистрация роутеров
dp.include_router(start.router)
dp.include_router(video.router)
dp.include_router(settings.router)
dp.include_router(help_handler.router)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    Обработка команды /start
    
    Args:
        message: Объект сообщения от пользователя
    """
    await start.start_handler(message)


@dp.message(Command("settings"))
async def command_settings_handler(message: Message) -> None:
    """
    Обработка команды /settings
    
    Args:
        message: Объект сообщения от пользователя
    """
    await settings.settings_handler(message)


@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    """
    Обработка команды /help
    
    Args:
        message: Объект сообщения от пользователя
    """
    await help_handler.help_handler(message)


@dp.message()
async def echo_handler(message: Message) -> None:
    """
    Обработка всех остальных сообщений
    
    Args:
        message: Объект сообщения от пользователя
    """
    try:
        await message.answer(
            f"👋 Привет, {html.bold(message.from_user.full_name)}!\n\n"
            f"Я REELFIX - бот для обработки видео.\n\n"
            f"Используй команды:\n"
            f"/start - Главное меню\n"
            f"/help - Справка\n"
            f"/settings - Настройки\n"
            f"/video - Обработка видео\n\n"
            f"Отправь мне видео, и я помогу его обработать!"
        )
    except Exception as e:
        logger.error(f"Ошибка в echo_handler: {e}")


async def main() -> None:
    """
    Основная функция запуска бота
    """
    try:
        # Проверка обязательных переменных
        config.validate()
        
        # Инициализация бота
        bot = Bot(
            token=config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        logger.info("🚀 REELFIX бот запущен!")
        
        # Запуск polling
        await dp.start_polling(bot)
        
    except ValueError as e:
        logger.error(f"❌ Ошибка конфигурации: {e}")
        print(f"\n❌ Ошибка: {e}")
        print("\nПожалуйста, добавьте BOT_TOKEN в переменные окружения!")
        return
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")