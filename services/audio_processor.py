"""
Сервис для обработки аудио (улучшение качества, удаление шума)
"""
import os
import subprocess
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AudioProcessor:
    """Сервис для обработки аудио с помощью FFmpeg и AI"""
    
    def __init__(self, ffmpeg_path: str = "/usr/bin/ffmpeg"):
        """
        Инициализация AudioProcessor
        
        Args:
            ffmpeg_path: Путь к FFmpeg
        """
        self.ffmpeg_path = ffmpeg_path
    
    def denoise_audio(
        self,
        input_path: str,
        output_path: str,
        noise_threshold: float = -40,
        reduction_factor: float = 0.5
    ) -> str:
        """
        Удаление шума из аудио
        
        Args:
            input_path: Путь к входному аудио
            output_path: Путь к выходному аудио
            noise_threshold: Порог шума (dB)
            reduction_factor: Коэффициент подавления шума (0-1)
            
        Returns:
            Путь к обработанному аудио
        """
        try:
            logger.info(f"Удаление шума (порог: {noise_threshold}dB)")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-af", f"highpass=f={noise_threshold},lowpass=f={noise_threshold + 10},afftdn=nf={reduction_factor * 100}",
                "-c:a", "libmp3lame",
                "-q:a", "2",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка удаления шума: {result.stderr}")
                raise RuntimeError(f"Ошибка удаления шума: {result.stderr}")
            
            logger.info(f"Шум удален: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка удаления шума: {e}")
            raise
    
    def enhance_audio(
        self,
        input_path: str,
        output_path: str,
        volume_boost: float = 0,
        normalize: bool = True,
        noise_reduction: bool = True
    ) -> str:
        """
        Улучшение качества аудио
        
        Args:
            input_path: Путь к входному аудио
            output_path: Путь к выходному аудио
            volume_boost: Усиление громкости (dB)
            normalize: Нормализация громкости
            noise_reduction: Удаление шума
            
        Returns:
            Путь к обработанному аудио
        """
        try:
            logger.info(f"Улучшение аудио")
            
            filters = []
            
            if volume_boost != 0:
                filters.append(f"volume={volume_boost}dB")
            
            if normalize:
                filters.append("loudnorm=I=-16:TP=-1.5:LRA=11")
            
            if noise_reduction:
                filters.append("highpass=f=200,lowpass=f=3000,afftdn=nf=0.5")
            
            filter_str = ",".join(filters)
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-af", filter_str,
                "-c:a", "libmp3lame",
                "-q:a", "2",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка улучшения аудио: {result.stderr}")
                raise RuntimeError(f"Ошибка улучшения аудио: {result.stderr}")
            
            logger.info(f"Аудио улучшено: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка улучшения аудио: {e}")
            raise
    
    def add_music(
        self,
        input_path: str,
        output_path: str,
        music_path: str,
        volume: float = 0.3,
        fade_in: float = 2.0,
        fade_out: float = 2.0
    ) -> str:
        """
        Добавление музыки к видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            music_path: Путь к музыкальному файлу
            volume: Громкость музыки (0-1)
            fade_in: Время затухания на входе (секунды)
            fade_out: Время затухания на выходе (секунды)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Добавление музыки")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-i", music_path,
                "-filter_complex",
                f"[1:a]volume={volume}[a1];[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]",
                "-map", "0:v",
                "-map", "[aout]",
                "-c:v", "libx264",
                "-c:a", "aac",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка добавления музыки: {result.stderr}")
                raise RuntimeError(f"Ошибка добавления музыки: {result.stderr}")
            
            logger.info(f"Музыка добавлена: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка добавления музыки: {e}")
            raise
    
    def extract_audio_from_video(self, input_path: str, output_path: str) -> str:
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
    
    def change_audio_format(
        self,
        input_path: str,
        output_path: str,
        output_format: str = "mp3"
    ) -> str:
        """
        Изменение формата аудио
        
        Args:
            input_path: Путь к входному аудио
            output_path: Путь к выходному аудио
            output_format: Целевой формат (mp3, wav, ogg, flac)
            
        Returns:
            Путь к обработанному аудио
        """
        try:
            logger.info(f"Конвертация аудио в {output_format}")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-c:a", f"lib{output_format}",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка конвертации аудио: {result.stderr}")
                raise RuntimeError(f"Ошибка конвертации аудио: {result.stderr}")
            
            logger.info(f"Аудио конвертировано: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка конвертации аудио: {e}")
            raise
    
    def normalize_volume(self, input_path: str, output_path: str, target_level: float = -16) -> str:
        """
        Нормализация громкости аудио
        
        Args:
            input_path: Путь к входному аудио
            output_path: Путь к выходному аудио
            target_level: Целевой уровень громкости (dB)
            
        Returns:
            Путь к обработанному аудио
        """
        try:
            logger.info(f"Нормализация громкости до {target_level}dB")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-af", f"loudnorm=I={target_level}:TP=-1.5:LRA=11",
                "-c:a", "libmp3lame",
                "-q:a", "2",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка нормализации громкости: {result.stderr}")
                raise RuntimeError(f"Ошибка нормализации громкости: {result.stderr}")
            
            logger.info(f"Громкость нормализована: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка нормализации громкости: {e}")
            raise
    
    def remove_silence(
        self,
        input_path: str,
        output_path: str,
        silence_threshold: float = -30,
        silence_duration: float = 0.5
    ) -> str:
        """
        Удаление тишины из аудио
        
        Args:
            input_path: Путь к входному аудио
            output_path: Путь к выходному аудио
            silence_threshold: Порог тишины (dB)
            silence_duration: Минимальная длительность тишины (секунды)
            
        Returns:
            Путь к обработанному аудио
        """
        try:
            logger.info(f"Удаление тишины")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-af", f"silenceremove=start_periods=1:start_silence={silence_duration}:start_threshold={silence_threshold}dB:stop_periods=-1:stop_silence={silence_duration}:stop_threshold={silence_threshold}dB",
                "-c:a", "libmp3lame",
                "-q:a", "2",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка удаления тишины: {result.stderr}")
                raise RuntimeError(f"Ошибка удаления тишины: {result.stderr}")
            
            logger.info(f"Тишина удалена: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка удаления тишины: {e}")
            raise
    
    def get_audio_info(self, audio_path: str) -> dict:
        """
        Получить информацию о аудио
        
        Args:
            audio_path: Путь к аудиофайлу
            
        Returns:
            Словарь с информацией об аудио
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", audio_path,
                "-hide_banner",
                "-loglevel", "error"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            info = {}
            for line in result.stderr.split('\n'):
                if 'Duration:' in line:
                    info['duration'] = line.split('Duration:')[1].split(',')[0].strip()
                if 'Stream #0:' in line and 'Audio:' in line:
                    info['audio'] = line
            
            return info
            
        except Exception as e:
            logger.error(f"Ошибка получения информации об аудио: {e}")
            raise
    
    def apply_audio_effects(
        self,
        input_path: str,
        output_path: str,
        effects: list
    ) -> str:
        """
        Применение аудио эффектов
        
        Args:
            input_path: Путь к входному аудио
            output_path: Путь к выходному аудио
            effects: Список эффектов (reverb, echo, bass_boost, treble_boost)
            
        Returns:
            Путь к обработанному аудио
        """
        try:
            logger.info(f"Применение аудио эффектов: {effects}")
            
            filter_str = ",".join(effects)
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-af", filter_str,
                "-c:a", "libmp3lame",
                "-q:a", "2",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка применения эффектов: {result.stderr}")
                raise RuntimeError(f"Ошибка применения эффектов: {result.stderr}")
            
            logger.info(f"Эффекты применены: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка применения эффектов: {e}")
            raise