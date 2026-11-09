"""
Сервис для работы с Whisper - автоматические субтитры
"""
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WhisperService:
    """Сервис для генерации субтитров с помощью Whisper AI"""

    def __init__(self, model_size: str = "base"):
        """
        Инициализация Whisper сервиса

        Args:
            model_size: Размер модели (tiny, base, small, medium, large)
        """
        self.model_size = model_size
        self.model = None
        # Модель НЕ загружаем в __init__: импорт whisper/torch и скачивание
        # модели на старте бота тормозят запуск и мешают Render открыть порт.
        # Загрузка происходит лениво при первом вызове transcribe/translate.

    def _load_model(self):
        """Загрузка модели Whisper (ленивый импорт whisper/torch)"""
        try:
            import whisper
            logger.info(f"Загрузка модели Whisper: {self.model_size}")
            self.model = whisper.load_model(self.model_size)
            logger.info("Модель Whisper успешно загружена")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели Whisper: {e}")
            raise

    def _ensure_model(self):
        """Загрузить модель при первом использовании"""
        if self.model is None:
            self._load_model()

    def transcribe(
        self,
        audio_path: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        verbose: bool = False
    ) -> Dict:
        """
        Транскрибация аудио в текст
        
        Args:
            audio_path: Путь к аудиофайлу
            language: Язык (ru, en, etc.)
            task: Задача (transcribe, translate)
            verbose: Показывать детали
            
        Returns:
            Словарь с результатами транскрибации
        """
        try:
            self._ensure_model()
            logger.info(f"Начало транскрибации: {audio_path}")
            
            result = self.model.transcribe(
                audio_path,
                language=language,
                task=task,
                verbose=verbose
            )
            
            logger.info(f"Транскрибация завершена: {len(result['segments'])} сегментов")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка транскрибации: {e}")
            raise

    def generate_subtitles(
        self,
        audio_path: str,
        language: str = "ru",
        output_format: str = "srt",
        style: str = "default"
    ) -> str:
        """
        Генерация субтитров в формате SRT
        
        Args:
            audio_path: Путь к аудиофайлу
            language: Язык
            output_format: Формат субтитров (srt, vtt)
            style: Стиль субтитров
            
        Returns:
            Путь к файлу с субтитрами
        """
        try:
            # Транскрибация
            result = self.transcribe(audio_path, language=language)
            
            # Генерация субтитров
            subtitles = self._format_subtitles(result, output_format, style)
            
            # Сохранение
            output_path = audio_path.rsplit('.', 1)[0] + f".{output_format}"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(subtitles)
            
            logger.info(f"Субтитры сохранены: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка генерации субтитров: {e}")
            raise

    def _format_subtitles(
        self,
        result: Dict,
        output_format: str,
        style: str
    ) -> str:
        """
        Форматирование субтитров
        
        Args:
            result: Результат транскрибации
            output_format: Формат субтитров (srt, vtt)
            style: Стиль
            
        Returns:
            Строка с субтитрами
        """
        if output_format == "srt":
            return self._format_srt(result, style)
        elif output_format == "vtt":
            return self._format_vtt(result, style)
        else:
            raise ValueError(f"Неподдерживаемый формат: {output_format}")

    def _format_srt(self, result: Dict, style: str) -> str:
        """Форматирование в SRT"""
        lines = []
        
        for i, segment in enumerate(result['segments'], 1):
            start = self._format_timestamp(segment['start'])
            end = self._format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            # Применение стилей
            text = self._apply_style(text, style)
            
            lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        
        return "\n".join(lines)

    def _format_vtt(self, result: Dict, style: str) -> str:
        """Форматирование в VTT"""
        lines = ["WEBVTT\n\n"]
        
        for i, segment in enumerate(result['segments'], 1):
            start = self._format_timestamp(segment['start'])
            end = self._format_timestamp(segment['end'])
            text = segment['text'].strip()
            
            # Применение стилей
            text = self._apply_style(text, style)
            
            lines.append(f"{start} --> {end}\n{text}\n")
        
        return "\n".join(lines)

    def _format_timestamp(self, seconds: float) -> str:
        """Форматирование времени в формат HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _apply_style(self, text: str, style: str) -> str:
        """Применение стиля к тексту"""
        # Базовые стили (можно расширить)
        styles = {
            "default": text,
            "bold": f"<b>{text}</b>",
            "italic": f"<i>{text}</i>",
            "bold-italic": f"<b><i>{text}</i></b>",
            "outline": f"<font color='white'>{text}</font>",
            "shadow": f"<font color='black'>{text}</font>",
            "neon": f"<font color='#00ffff'>{text}</font>",
            "gold": f"<font color='#ffd700'>{text}</font>",
            "red": f"<font color='#ff0000'>{text}</font>",
            "blue": f"<font color='#0000ff'>{text}</font>",
        }
        
        return styles.get(style, text)

    def translate(self, audio_path: str, target_language: str = "en") -> Dict:
        """
        Перевод аудио на другой язык
        
        Args:
            audio_path: Путь к аудиофайлу
            target_language: Целевой язык
            
        Returns:
            Результат перевода
        """
        try:
            logger.info(f"Перевод аудио на {target_language}")
            
            result = self.transcribe(
                audio_path,
                language=None,  # Автоопределение языка
                task="translate"
            )
            
            logger.info("Перевод завершен")
            return result
            
        except Exception as e:
            logger.error(f"Ошибка перевода: {e}")
            raise

    def get_available_models(self) -> List[str]:
        """Получить список доступных моделей"""
        return ["tiny", "base", "small", "medium", "large"]

    def set_model(self, model_size: str):
        """Сменить модель"""
        if model_size not in self.get_available_models():
            raise ValueError(f"Неподдерживаемая модель: {model_size}")
        
        self.model_size = model_size
        # Если модель уже была загружена — перезагружаем, иначе отложим до первого вызова
        if self.model is not None:
            self._load_model()
        logger.info(f"Модель изменена на: {model_size}")
