"""
字体管理模块

提供字体的创建和管理功能，支持字体属性的设置和更新。
包括字体族、字号、字重、斜体和下划线等属性的管理。
"""

from tkinter.font import Font
from typing import Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class FontManager:
    """
    字体管理类
    
    提供字体相关功能，包括：
    - 字体创建
    - 属性管理
    - 默认字体设置
    
    Attributes:
        default_family: 默认字体族
        default_size: 默认字号
        _current_font: 当前字体对象
    """
    
    def __init__(self):
        """初始化字体管理器"""
        logger.info("初始化字体管理器")
        self.default_family = 'Times New Roman'
        self.default_size = 12
        self._current_font: Optional[Font] = None
        logger.debug(f"设置默认字体: {self.default_family}, 字号: {self.default_size}")

    def create_font(self, family: Optional[str] = None, size: Optional[int] = None,
                   weight: str = 'normal', slant: str = 'roman', underline: bool = False) -> Font:
        """
        创建字体对象
        
        根据指定的属性创建新的字体对象。如果未指定某些属性，
        将使用默认值。
        
        Args:
            family: 字体族
            size: 字号
            weight: 字重（'normal' 或 'bold'）
            slant: 斜体（'roman' 或 'italic'）
            underline: 是否添加下划线
            
        Returns:
            Font: 字体对象
        """
        logger.debug(
            f"创建字体 - 字体族: {family or self.default_family}, "
            f"字号: {size or self.default_size}, "
            f"字重: {weight}, 斜体: {slant}, 下划线: {underline}"
        )
        
        return Font(
            family=family or self.default_family,
            size=size or self.default_size,
            weight=weight,
            slant=slant,
            underline=underline
        )

    @property
    def current_font(self) -> Font:
        """
        获取当前字体
        
        如果当前字体未设置，将创建一个使用默认属性的字体对象。
        
        Returns:
            Font: 当前字体对象
        """
        if not self._current_font:
            logger.debug("创建默认字体对象")
            self._current_font = self.create_font()
        return self._current_font

    def update_current_font(self, **kwargs):
        """
        更新当前字体属性
        
        更新当前字体的一个或多个属性。
        
        Args:
            **kwargs: 要更新的属性和值
                可用属性包括：family, size, weight, slant, underline
        """
        if self._current_font:
            logger.debug(f"更新字体属性: {kwargs}")
            for key, value in kwargs.items():
                self._current_font[key] = value
        else:
            logger.warning("当前字体未初始化，无法更新属性") 