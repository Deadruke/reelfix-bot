"""
Сервис для улучшения качества видео (AI upscaling, цветокоррекция)
"""
import os
import subprocess
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class QualityEnhancer:
    """Сервис для улучшения качества видео с помощью AI и FFmpeg"""
    
    def __init__(self, ffmpeg_path: str = "/usr/bin/ffmpeg"):
        """
        Инициализация QualityEnhancer
        
        Args:
            ffmpeg_path: Путь к FFmpeg
        """
        self.ffmpeg_path = ffmpeg_path
    
    def upscale_video(
        self,
        input_path: str,
        output_path: str,
        scale_factor: int = 2,
        algorithm: str = "bicubic"
    ) -> str:
        """
        Увеличение разрешения видео (Upscaling)
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            scale_factor: Коэффициент масштабирования (2x, 4x)
            algorithm: Алгоритм масштабирования (bicubic, lanczos, bilinear)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Upscaling видео: {scale_factor}x")
            
            # Получаем размер входного видео
            cmd_info = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", "scale=iw:ih:flags=flags",
                "-f", "null",
                "-"
            ]
            
            result = subprocess.run(cmd_info, capture_output=True, text=True)
            
            # Определяем флаги для масштабирования
            flags_map = {
                "bicubic": "flags=bicubic",
                "lanczos": "flags=lanczos",
                "bilinear": "flags=bilinear"
            }
            
            flags = flags_map.get(algorithm, "flags=bicubic")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", f"scale=iw*{scale_factor}:ih*{scale_factor}:{flags}",
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", "18",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка upsampling: {result.stderr}")
                raise RuntimeError(f"Ошибка upsampling: {result.stderr}")
            
            logger.info(f"Видео upscaled: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка upsampling видео: {e}")
            raise
    
    def enhance_colors(
        self,
        input_path: str,
        output_path: str,
        brightness: float = 0,
        contrast: float = 0,
        saturation: float = 0,
        sharpness: float = 0
    ) -> str:
        """
        Цветокоррекция видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            brightness: Яркость (-100 до 100)
            contrast: Контраст (-100 до 100)
            saturation: Насыщенность (-100 до 100)
            sharpness: Резкость (-100 до 100)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Цветокоррекция: B={brightness}, C={contrast}, S={saturation}, Sharp={sharpness}")
            
            filters = []
            
            if brightness != 0:
                filters.append(f"eq=brightness={brightness/100}")
            
            if contrast != 0:
                filters.append(f"eq=contrast={1 + contrast/100}")
            
            if saturation != 0:
                filters.append(f"eq=saturation={1 + saturation/100}")
            
            if sharpness != 0:
                filters.append(f"unsharp=lc={sharpness/10}:ls={sharpness/10}:hc={sharpness/10}:hs={sharpness/10}")
            
            filter_str = ",".join(filters)
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", filter_str,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка цветокоррекции: {result.stderr}")
                raise RuntimeError(f"Ошибка цветокоррекции: {result.stderr}")
            
            logger.info(f"Цветокоррекция применена: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка цветокоррекции видео: {e}")
            raise
    
    def denoise_video(
        self,
        input_path: str,
        output_path: str,
        strength: float = 0.5
    ) -> str:
        """
        Удаление шума из видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            strength: Сила шумоподавления (0-1)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Удаление шума (сила: {strength})")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", f"hqdn3d=0:{strength}",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-c:a", "copy",
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
            logger.error(f"Ошибка удаления шума видео: {e}")
            raise
    
    def apply_stabilization(
        self,
        input_path: str,
        output_path: str,
        strength: float = 0.5
    ) -> str:
        """
        Стабилизация видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            strength: Сила стабилизации (0-1)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Стабилизация видео (сила: {strength})")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", f"vidstabdetect=shakiness={strength}:accuracy=15:stepsize=6:result=transforms.trf",
                "-f", "null",
                "-"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка детекции дрожания: {result.stderr}")
                raise RuntimeError(f"Ошибка детекции дрожания: {result.stderr}")
            
            # Применяем стабилизацию
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", f"vidstabtransform=smoothing={strength*10}:input='transforms.trf':interpol='bilinear'",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка стабилизации: {result.stderr}")
                raise RuntimeError(f"Ошибка стабилизации: {result.stderr}")
            
            logger.info(f"Видео стабилизировано: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка стабилизации видео: {e}")
            raise
    
    def enhance_resolution(
        self,
        input_path: str,
        output_path: str,
        target_resolution: str = "1080p"
    ) -> str:
        """
        Улучшение разрешения видео до целевого
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            target_resolution: Целевое разрешение (720p, 1080p, 4k)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Улучшение разрешения до {target_resolution}")
            
            resolution_map = {
                "720p": (1280, 720),
                "1080p": (1920, 1080),
                "4k": (3840, 2160)
            }
            
            width, height = resolution_map.get(target_resolution, (1920, 1080))
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", f"scale={width}:{height}:flags=lanczos",
                "-c:v", "libx264",
                "-preset", "slow",
                "-crf", "18",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка улучшения разрешения: {result.stderr}")
                raise RuntimeError(f"Ошибка улучшения разрешения: {result.stderr}")
            
            logger.info(f"Разрешение улучшено: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка улучшения разрешения видео: {e}")
            raise
    
    def apply_filters(
        self,
        input_path: str,
        output_path: str,
        filters: list
    ) -> str:
        """
        Применение фильтров к видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            filters: Список фильтров (grayscale, sepia, vignette, etc.)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Применение фильтров: {filters}")
            
            filter_str = ",".join(filters)
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", filter_str,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка применения фильтров: {result.stderr}")
                raise RuntimeError(f"Ошибка применения фильтров: {result.stderr}")
            
            logger.info(f"Фильтры применены: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка применения фильтров видео: {e}")
            raise
    
    def enhance_sharpness(
        self,
        input_path: str,
        output_path: str,
        strength: float = 1.0
    ) -> str:
        """
        Улучшение резкости видео
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            strength: Сила резкости (0-1)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Улучшение резкости (сила: {strength})")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", f"unsharp=lc={strength}:ls={strength}:hc={strength}:hs={strength}",
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка улучшения резкости: {result.stderr}")
                raise RuntimeError(f"Ошибка улучшения резкости: {result.stderr}")
            
            logger.info(f"Резкость улучшена: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка улучшения резкости видео: {e}")
            raise
    
    def apply_color_grade(
        self,
        input_path: str,
        output_path: str,
        grade: str = "cinematic"
    ) -> str:
        """
        Применение цветовой грейды
        
        Args:
            input_path: Путь к входному видео
            output_path: Путь к выходному видео
            grade: Тип грейды (cinematic, warm, cool, vintage, etc.)
            
        Returns:
            Путь к обработанному видео
        """
        try:
            logger.info(f"Применение цветовой грейды: {grade}")
            
            grade_map = {
                "cinematic": "eq=brightness=-0.1:contrast=1.2:saturation=1.1",
                "warm": "eq=brightness=0:contrast=1:saturation=1.2",
                "cool": "eq=brightness=0:contrast=1:saturation=0.9",
                "vintage": "eq=brightness=0:contrast=1.1:saturation=0.8",
                "dramatic": "eq=brightness=-0.2:contrast=1.3:saturation=1.2",
                "bright": "eq=brightness=0.1:contrast=1:saturation=1"
            }
            
            filter_str = grade_map.get(grade, grade_map["cinematic"])
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-vf", filter_str,
                "-c:v", "libx264",
                "-preset", "medium",
                "-crf", "18",
                "-c:a", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Ошибка применения цветовой грейды: {result.stderr}")
                raise RuntimeError(f"Ошибка применения цветовой грейды: {result.stderr}")
            
            logger.info(f"Цветовая грейда применена: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Ошибка применения цветовой грейды видео: {e}")
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
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            info = {}
            for line in result.stderr.split('\n'):
                if 'Duration:' in line:
                    info['duration'] = line.split('Duration:')[1].split(',')[0].strip()
                if 'Stream #0:' in line and 'Video:' in line:
                    info['video'] = line
            
            return info
            
        except Exception as e:
            logger.error(f"Ошибка получения информации о видео: {e}")
            raise