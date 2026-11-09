"""
Точка входа для Render.
Start Command в дашборде был настроен как 'Python bot.py',
поэтому добавляем bot.py, который запускает main.main().
ВАЖНО: в дашборде команду нужно писать с маленькой буквы:
    python main.py
или
    python bot.py
Команда 'Python' (с большой) на Linux не находится.
"""
import asyncio
import logging

from main import main

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
