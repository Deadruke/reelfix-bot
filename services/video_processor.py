"""
Сервис для обработки видео (обрезка, изменение формата, удаление пауз)
"""
import os
import subprocess
from typing import Optional, Tuple, List
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Сервис для обработки видео с помощью FFmpeg"""
    
    def __init__(self, ffmpeg_path: str = "/usr/bin/ffmpeg"):
        """
        Инициализация VideoProcessor
        
        Args:
            ffmpeg_path: Путь к FFmpeg
        """
        self.ffmpeg_path = ffmpeg_path
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Проверка наличия FFmpeg"""
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError("FFmpeg не найден или не работает")
            logger.info("FFmpeg успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка инициализации FFmpeg: {e}")
            raise
    
    def get_video_info(self, video_path: str) -> dict:
        """
        Получить информацию о видео
        
        Args:
            video_path: Путь к видео файлу
            
        Returns:
            Словарь с информацией о видео
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-hide_banner",
                "-loglevel", "error"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            info = {}
            for line in result.stderr.split('\n'):
                if 'Duration:' in line:
                    info['duration'] = self._parse_duration(line.split('Duration:')[1].split(',')[0])
                if 'Stream #0:' in line and 'Video:' in line:
                    parts = line.split(',')
                    for part in parts:
                        if 'Duration:' in part:
                            info['duration'] = self._parse_duration(part.split('Duration:')[1].split(',')[0])
                        if 'Video:' in part:
                            info['video'] = part
                        if 'Audio:' in part:
                            info['audio'] = part
            
            return info
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о видео: {e}")
            raise
    
    def _parse_duration(self, duration_str: str) -> float:
        """Парсинг длительности из строки"""
        try:
            parts = duration_str.split(':')
            if len(parts) == 3:
                h, m, s = map(float, parts)
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m, s = map(float, parts)
                return m * 60 + s
            else:
                return float(parts[0])
        except:
            return 0.0
    
    def trim_video(
        self,
        input_path: str,
        output_path: str,
        start_time: float = 0,
        end_time: Optional[float] = None,
        keep_audio: bool = True
    ) -> str:
        """
        Обрезка видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            start_time: Начальное время (секунды)
            end_time: Конечное время (секунды), None = до конца
            keep_audio: Сохранять аудио
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Обрезка видео: {start_time}s - {end_time or 'конец'}")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-ss", str(start_time)
            ]
            
            if end_time:
                cmd.extend(["-to", str(end_time)])
            
            cmd.extend([
                "-c:v", "libx264",
                "-c:a", "aac" if keep_audio else "copy",
                "-y",
                output_path
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка обрезки видео: {result.stderr}")
                raise RuntimeError(f"Ошибка обрезки видео: {result.stderr}")
            
            logger.info(f"Видео обрезано: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка обрезки видео: {e}")
            raise
    
    def change_format(
        self,
        input_path: str,
        output_path: str,
        output_format: str = "mp4",
        quality: str = "high"
    ) -> str:
        """
        Изменение формата видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            output_format: Целевой формат (mp4, webm, mov, avi)
            quality: Качество (low, medium, high)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Конвертация в формат {output_format}")
            
            # Настройки качества
            quality_settings = {
                "low": {"crf": "28", "preset": "fast"},
                "medium": {"crf": "23", "preset": "medium"},
                "high": {"crf": "18", "preset": "slow"}
            }
            
            settings = quality_settings.get(quality, quality_settings["high"])
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-c:v", "libx264",
                "-crf", settings["crf"],
                "-preset", settings["preset"],
                "-c:a", "aac",
                "-b:a", "192k",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка конвертации: {result.stderr}")
                raise RuntimeError(f"Ошибка конвертации: {result.stderr}")
            
            logger.info(f"Видео конвертировано: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка конвертации видео: {e}")
            raise
    
    def resize_video(
        self,
        input_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        aspect_ratio: str = "original",
        maintain_aspect: bool = True
    ) -> str:
        """
        Изменение размера видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            width: Ширина в пикселях
            height: Высота в пикселях
            aspect_ratio: Соотношение сторон (original, 16:9, 9:16, 1:1)
            maintain_aspect: Сохранять соотношение сторон
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Изменение размера видео")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y"
            ]
            
            # Расчет размеров
            if aspect_ratio != "original":
                if aspect_ratio == "16:9":
                    width, height = 1920, 1080
                elif aspect_ratio == "9:16":
                    width, height = 1080, 1920
                elif aspect_ratio == "1:1":
                    width, height = 1080, 1080
                else:
                    width, height = 1280, 720
            
            if width and height:
                if maintain_aspect:
                    cmd.extend(["-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"])
                else:
                    cmd.extend(["-vf", f"scale={width}:{height}"])
            elif width:
                cmd.extend(["-vf", f"scale={width}:-2"])
            elif height:
                cmd.extend(["-vf", f"scale=-2:{height}"])
            
            cmd.append(output_path)
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка изменения размера: {result.stderr}")
                raise RuntimeError(f"Ошибка изменения размера: {result.stderr}")
            
            logger.info(f"Размер изменен: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка изменения размера видео: {e}")
            raise
    
    def remove_pauses(
        self,
        input_path: str,
        output_path: str,
        silence_threshold: float = -30,
        silence_duration: float = 0.5
    ) -> str:
        """
        Удаление пауз из видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            silence_threshold: Порог тишины (dB)
            silence_duration: Минимальная длительность тишины для удаления (секунды)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Удаление пауз (порог: {silence_threshold}dB, длительность: {silence_duration}s)")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-af", f"silenceremove=start_periods=1:start_silence={silence_duration}:start_threshold={silence_threshold}dB:stop_periods=-1:stop_silence={silence_duration}:stop_threshold={silence_threshold}dB",
                "-c:v", "copy",
                "-c:a", "aac",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка удаления пауз: {result.stderr}")
                raise RuntimeError(f"Ошибка удаления пауз: {result.stderr}")
            
            logger.info(f"Паузы удалены: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка удаления пауз: {e}")
            raise
    
    def add_watermark(
        self,
        input_path: str,
        output_path: str,
        watermark_path: str,
        position: str = "bottom-right",
        opacity: float = 0.5,
        size: float = 0.2
    ) -> str:
        """
        Добавление водяного знака
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            watermark_path: Путь к водяному знаку
            position: Позиция (top-left, top-right, bottom-left, bottom-right, center)
            opacity: Прозрачность (0-1)
            size: Размер относительно видео (0-1)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Добавление водяного знака")
            
            # Расчет позиции
            position_map = {
                "top-left": "x=(w-wi)*0:y=(h-hi)*0",
                "top-right": "x=(w-wi)*1:y=(h-hi)*0",
                "bottom-left": "x=(w-wi)*0:y=(h-hi)*1",
                "bottom-right": "x=(w-wi)*1:y=(h-hi)*1",
                "center": "x=(w-wi)/2:y=(h-hi)/2"
            }
            
            pos = position_map.get(position, position_map["bottom-right"])
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-i", watermark_path,
                "-filter_complex",
                f"[1:v]format=rgba,colorchannelmixer=aa={opacity}[wm];[0:v][wm]overlay={pos}",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка добавления водяного знака: {result.stderr}")
                raise RuntimeError(f"Ошибка добавления водяного знака: {result.stderr}")
            
            logger.info(f"Водяной знак добавлен: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка добавления водяного знака: {e}")
            raise
    
    def extract_audio(self, input_path: str, output_path: str) -> str:
        """
        Извлечение аудио из видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному аудио
            
        Returns:
            Путь к аудиофайлу
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vn",
                "-acodec", "libmp3lame",
                "-q:a", "2",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка извлечения аудио: {result.stderr}")
                raise RuntimeError(f"Ошибка извлечения аудио: {result.stderr}")
            
            logger.info(f"Аудио извлечено: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка извлечения аудио: {e}")
            raise
    
    def merge_videos(self, input_paths: List[str], output_path: str) -> str:
        """
        Слияние нескольких видео файлов
        
        Args:
            input_paths: Список путей к видео
            output_path: Путь к выходному видео
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Слияние {len(input_paths)} видео файлов")
            
            # Создание временного файла с последовательностью
            concat_file = "concat_list.txt"
            with open(concat_file, 'w', encoding='utf-8') as f:
                for path in input_paths:
                    f.write(f"file '{path}'\n")
            
            cmd = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Удаление временного файла
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            if result.returncode != 0:
                logger.error(f"Ошибка слияния видео: {result.stderr}")
                raise RuntimeError(f"Ошибка слияния видео: {result.stderr}")
            
            logger.info(f"Видео успешно объединены: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка слияния видео: {e}")
            raise
    
    def get_supported_formats(self) -> List[str]:
        """Получить список поддерживаемых форматов"""
        return ["mp4", "webm", "mov", "avi", "mkv", "flv", "wmv", "m4v"]