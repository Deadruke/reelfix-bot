"""
REELFIX - Telegram Bot для обработки видео
Автор: Gubka-GPT
"""
import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from handlers import start, video, settings, help as help_handler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Инициализация диспетчера с явным FSM-хранилищем.
# Без storage FSM (FSMContext в handlers/video.py) может не работать.
dp = Dispatcher(storage=MemoryStorage())


# Регистрация роутеров.
# ВАЖНО: обработчики на уровне Dispatcher (@dp.message) в aiogram
# проверяются ПЕРЕД роутерами. Поэтому echo_handler нельзя вешать
# на dp — он перехватит ВСЕ сообщения (включая видео) и роутер
# handlers/video.py никогда не сработает. Fallback-роутер подключаем
# ПОСЛЕДНИМ, чтобы он был именно запасным.
dp.include_router(start.router)
dp.include_router(video.router)
dp.include_router(settings.router)
dp.include_router(help_handler.router)

fallback_router = Router()


@fallback_router.message()
async def echo_handler(message: Message) -> None:
    """
    Fallback-обработчик всех остальных сообщений.
    Срабатывает только если ни один роутер выше не обработал апдейт.

    Args:
        message: Объект сообщения от пользователя
    """
    try:
        user_name = message.from_user.full_name if message.from_user else "друг"
        await message.answer(
            f"👋 Привет, {html.bold(user_name)}!\n\n"
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


dp.include_router(fallback_router)


# --- Health server for Render (web_service requires open PORT) ---

async def _health_handler(request):
    try:
        from aiohttp import web
        return web.Response(text="OK", status=200)
    except Exception:
        return None


async def start_health_server():
    """
    Запуск лёгкого HTTP health-сервера на PORT (Render).
    Нужен, потому что сервис создан как web_service и без открытого
    порта Render помечает деплой как update_failed: No open ports detected.
    Возвращает runner (aiohttp) или None при fallback на stdlib.
    """
    port = int(os.getenv("PORT", "10000"))
    host = "0.0.0.0"

    # Основной путь: aiohttp (зависимость aiogram, теперь явно в requirements)
    try:
        from aiohttp import web

        async def health(request):
            return web.Response(text="OK", status=200)

        app = web.Application()
        app.router.add_get("/", health)
        app.router.add_get("/health", health)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        logger.info(f"✅ Health server listening on {host}:{port}")
        return runner
    except Exception as e:
        logger.warning(f"aiohttp health server failed ({e}), fallback to stdlib")

    # Fallback: stdlib http.server в отдельном потоке
    try:
        from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
        import threading

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(b"OK")

            def log_message(self, format, *args):
                return

        server = ThreadingHTTPServer((host, port), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        logger.info(f"✅ Health server (stdlib) listening on {host}:{port}")
        # Сохраняем ссылку, чтобы не потерять объект
        start_health_server._stdlib_server = server
        return None
    except Exception as e:
        logger.error(f"❌ Не удалось запустить health server: {e}")
        return None


async def main() -> None:
    """
    Основная функция запуска бота
    """
    health_runner = None
    try:
        # Health server запускаем ПЕРВЫМ, чтобы Render сразу видел открытый порт,
        # даже пока импортируются тяжёлые зависимости / инициализируется бот
        health_runner = await start_health_server()

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
    finally:
        if health_runner is not None:
            try:
                await health_runner.cleanup()
            except Exception:
                pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
