"""
Сервис для генерации субтитров с разными стилями
"""
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class SubtitleGenerator:
    """Сервис для генерации субтитров с различными стилями"""
    
    # 10+ стилей субтитров как в CapCut
    STYLES = {
        "default": {
            "font": "Arial",
            "size": 24,
            "color": "#FFFFFF",
            "background": "#00000080",
            "outline": 1,
            "shadow": 0,
            "position": "bottom"
        },
        "bold": {
            "font": "Arial Black",
            "size": 24,
            "color": "#FFFFFF",
            "background": "#00000080",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "italic": {
            "font": "Arial Italic",
            "size": 24,
            "color": "#FFFFFF",
            "background": "#00000080",
            "outline": 1,
            "shadow": 0,
            "position": "bottom"
        },
        "bold-italic": {
            "font": "Arial Bold Italic",
            "size": 24,
            "color": "#FFFFFF",
            "background": "#00000080",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "outline": {
            "font": "Arial",
            "size": 24,
            "color": "#FFFFFF",
            "background": "none",
            "outline": 3,
            "shadow": 0,
            "position": "bottom"
        },
        "shadow": {
            "font": "Arial",
            "size": 24,
            "color": "#FFFFFF",
            "background": "none",
            "outline": 0,
            "shadow": 2,
            "position": "bottom"
        },
        "neon": {
            "font": "Arial",
            "size": 24,
            "color": "#00FFFF",
            "background": "none",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "gold": {
            "font": "Arial",
            "size": 24,
            "color": "#FFD700",
            "background": "none",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "red": {
            "font": "Arial",
            "size": 24,
            "color": "#FF0000",
            "background": "none",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "blue": {
            "font": "Arial",
            "size": 24,
            "color": "#0000FF",
            "background": "none",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "green": {
            "font": "Arial",
            "size": 24,
            "color": "#00FF00",
            "background": "none",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "purple": {
            "font": "Arial",
            "size": 24,
            "color": "#800080",
            "background": "none",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "white": {
            "font": "Arial",
            "size": 24,
            "color": "#FFFFFF",
            "background": "none",
            "outline": 0,
            "shadow": 0,
            "position": "bottom"
        },
        "black": {
            "font": "Arial",
            "size": 24,
            "color": "#000000",
            "background": "#FFFFFF80",
            "outline": 0,
            "shadow": 0,
            "position": "bottom"
        },
        "large": {
            "font": "Arial",
            "size": 36,
            "color": "#FFFFFF",
            "background": "#00000080",
            "outline": 2,
            "shadow": 1,
            "position": "bottom"
        },
        "small": {
            "font": "Arial",
            "size": 18,
            "color": "#FFFFFF",
            "background": "#00000080",
            "outline": 1,
            "shadow": 0,
            "position": "bottom"
        }
    }
    
    def __init__(self):
        """Инициализация SubtitleGenerator"""
        self.available_styles = list(self.STYLES.keys())
    
    def generate_srt(
        self,
        subtitles: List[Dict],
        style: str = "default",
        output_path: Optional[str] = None
    ) -> str:
        """
        Генерация SRT субтитров
        
        Args:
            subtitles: Список словарей с текстом и временными метками
            style: Стиль субтитров
            output_path: Путь для сохранения (если None, вернет строку)
            
        Returns:
            Путь к файлу или строка с субтитрами
        """
        try:
            style_config = self.STYLES.get(style, self.STYLES["default"])
            
            lines = []
            lines.append(f"Style: {style_config['font']},{style_config['size']},"
                        f"{style_config['color']},"
                        f"{style_config['background']},"
                        f"{style_config['outline']},"
                        f"{style_config['shadow']},"
                        f"0,0,0,0,100,100")
            
            for i, sub in enumerate(subtitles, 1):
                start = self._format_timestamp(sub['start'])
                end = self._format_timestamp(sub['end'])
                text = sub['text']
                
                # Применяем стиль к тексту
                text = self._apply_style_to_text(text, style_config)
                
                lines.append(f"{i}\n{start} --> {end}\n{text}\n")
            
            srt_content = "\n".join(lines)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                logger.info(f"SRT субтитры сохранены: {output_path}")
                return output_path
            else:
                return srt_content
                
        except Exception as e:
            logger.error(f"Ошибка генерации SRT: {e}")
            raise
    
    def generate_vtt(
        self,
        subtitles: List[Dict],
        style: str = "default",
        output_path: Optional[str] = None
    ) -> str:
        """
        Генерация VTT субтитров
        
        Args:
            subtitles: Список словарей с текстом и временными метками
            style: Стиль субтитров
            output_path: Путь для сохранения (если None, вернет строку)
            
        Returns:
            Путь к файлу или строка с субтитрами
        """
        try:
            style_config = self.STYLES.get(style, self.STYLES["default"])
            
            lines = ["WEBVTT\n\n"]
            lines.append(f"Style: {style_config['font']},{style_config['size']},"
                        f"{style_config['color']},"
                        f"{style_config['background']},"
                        f"{style_config['outline']},"
                        f"{style_config['shadow']},"
                        f"0,0,0,0,100,100")
            
            for i, sub in enumerate(subtitles, 1):
                start = self._format_timestamp(sub['start'])
                end = self._format_timestamp(sub['end'])
                text = sub['text']
                
                # Применяем стиль к тексту
                text = self._apply_style_to_text(text, style_config)
                
                lines.append(f"{start} --> {end}\n{text}\n")
            
            vtt_content = "\n".join(lines)
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(vtt_content)
                logger.info(f"VTT субтитры сохранены: {output_path}")
                return output_path
            else:
                return vtt_content
                
        except Exception as e:
            logger.error(f"Ошибка генерации VTT: {e}")
            raise
    
    def _format_timestamp(self, seconds: float) -> str:
        """Форматирование времени в формат HH:MM:SS,mmm"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _apply_style_to_text(self, text: str, style_config: dict) -> str:
        """Применение стиля к тексту"""
        # Для SRT/VTT используем теги
        if style_config['background'] != 'none':
            text = f"<font color='{style_config['color']}' bg='{style_config['background']}'>{text}</font>"
        else:
            text = f"<font color='{style_config['color']}'>{text}</font>"
        
        return text
    
    def get_available_styles(self) -> List[str]:
        """Получить список доступных стилей"""
        return self.available_styles
    
    def get_style_info(self, style: str) -> Optional[dict]:
        """Получить информацию о стиле"""
        return self.STYLES.get(style)
    
    def create_subtitle_file(
        self,
        subtitles: List[Dict],
        format: str = "srt",
        style: str = "default",
        output_path: Optional[str] = None
    ) -> str:
        """
        Создание файла субтитров
        
        Args:
            subtitles: Список словарей с текстом и временными метками
            format: Формат (srt, vtt)
            style: Стиль субтитров
            output_path: Путь для сохранения
            
        Returns:
            Путь к файлу
        """
        try:
            if format == "srt":
                return self.generate_srt(subtitles, style, output_path)
            elif format == "vtt":
                return self.generate_vtt(subtitles, style, output_path)
            else:
                raise ValueError(f"Неподдерживаемый формат: {format}")
                
        except Exception as e:
            logger.error(f"Ошибка создания файла субтитров: {e}")
            raise
    
    def merge_subtitles(
        self,
        subtitles_list: List[List[Dict]],
        output_path: str
    ) -> str:
        """
        Объединение нескольких списков субтитров
        
        Args:
            subtitles_list: Список списков субтитров
            output_path: Путь для сохранения
            
        Returns:
            Путь к файлу
        """
        try:
            all_subtitles = []
            for subs in subtitles_list:
                all_subtitles.extend(subs)
            
            return self.generate_srt(all_subtitles, "default", output_path)
            
        except Exception as e:
            logger.error(f"Ошибка объединения субтитров: {e}")
            raise
    
    def format_subtitles_for_video(
        self,
        subtitles: List[Dict],
        video_width: int,
        video_height: int,
        style: str = "default"
    ) -> str:
        """
        Форматирование субтитров для встраивания в видео
        
        Args:
            subtitles: Список словарей с текстом и временными метками
            video_width: Ширина видео
            video_height: Высота видео
            style: Стиль субтитров
            
        Returns:
            Строка с форматированными субтитрами
        """
        try:
            style_config = self.STYLES.get(style, self.STYLES["default"])
            
            lines = []
            
            for i, sub in enumerate(subtitles, 1):
                start = self._format_timestamp(sub['start'])
                end = self._format_timestamp(sub['end'])
                text = sub['text']
                
                # Применяем стиль к тексту
                text = self._apply_style_to_text(text, style_config)
                
                # Определяем позицию
                position = self._get_position(style_config['position'], video_width, video_height)
                
                lines.append(f"{i}\n{start} --> {end}\n{text}\n")
            
            return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Ошибка форматирования субтитров: {e}")
            raise
    
    def _get_position(self, position: str, width: int, height: int) -> str:
        """Получить координаты позиции"""
        if position == "top":
            return f"x=(w-tw)/2:y=0"
        elif position == "top-left":
            return f"x=0:y=0"
        elif position == "top-right":
            return f"x=w-tw:y=0"
        elif position == "bottom":
            return f"x=(w-tw)/2:y=h-th"
        elif position == "bottom-left":
            return f"x=0:y=h-th"
        elif position == "bottom-right":
            return f"x=w-tw:y=h-th"
        elif position == "center":
            return f"x=(w-tw)/2:y=(h-th)/2"
        else:
            return f"x=(w-tw)/2:y=h-th"  # bottom by default