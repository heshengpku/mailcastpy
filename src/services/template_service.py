"""
模板处理服务模块

提供邮件模板的处理功能，包括变量替换、HTML格式转换、
参数验证等功能。
"""

from typing import Dict, Set, Tuple
import re
from src.utils.logger import setup_logger
import html

logger = setup_logger(__name__)

class TemplateService:
    """
    模板处理服务类
    
    提供模板相关的功能，包括：
    - 模板数据管理
    - 变量替换
    - HTML格式转换
    - 参数验证
    - 参数提取
    
    Attributes:
        _subject: 邮件主题
        _content: 邮件正文
        _is_html: 是否为HTML格式
        _tags: 富文本格式标签
        _font_family: 字体族
        _font_size: 字号
    """
    
    def __init__(self):
        """初始化模板服务"""
        logger.info("初始化模板服务")
        self._subject = ""
        self._content = ""
        self._is_html = True
        self._tags = {}
        self._font_family = "Times New Roman"
        self._font_size = "12"
    
    def update_template(self, subject: str, content: str, is_html: bool,
                       tags: Dict[str, list], font_family: str,
                       font_size: str) -> None:
        """
        更新模板数据
        
        Args:
            subject: 邮件主题
            content: 邮件正文
            is_html: 是否为HTML格式
            tags: 富文本格式标签
            font_family: 字体族
            font_size: 字号
        """
        logger.info("更新模板数据")
        self._subject = subject
        self._content = content
        self._is_html = is_html
        self._tags = tags
        self._font_family = font_family
        self._font_size = font_size
        logger.debug(f"模板更新完成 - 格式: {'HTML' if is_html else '纯文本'}")
    
    def get_template(self) -> Dict[str, any]:
        """
        获取当前模板数据
        
        Returns:
            Dict[str, any]: 包含模板所有数据的字典
        """
        return {
            'subject': self._subject,
            'content': self._content,
            'is_html': self._is_html,
            'tags': self._tags,
            'font_family': self._font_family,
            'font_size': self._font_size
        }
    
    def clear_template(self) -> None:
        """清空模板数据"""
        logger.info("清空模板数据")
        self._subject = ""
        self._content = ""
        self._is_html = True
        self._tags = {}
        self._font_family = "Times New Roman"
        self._font_size = "12"

    @staticmethod
    def replace_variables(template: str, variables: Dict[str, str]) -> str:
        """
        替换模板中的变量
        
        将模板中的 {变量名} 替换为对应的值。
        
        Args:
            template: 包含变量的模板字符串
            variables: 变量名和值的字典
            
        Returns:
            str: 替换变量后的字符串
        """
        logger.debug(f"替换模板变量 - 变量列表: {list(variables.keys())}")
        result = template
        for key, value in variables.items():
            result = result.replace('{' + key + '}', value)
        return result

    def get_html_content(self) -> str:
        """
        将文本内容转换为HTML格式

        根据标签信息将纯文本转换为带格式的HTML。支持对选中文本段落设置不同的格式，
        并对HTML中保留原始文本的空格和换行。

        Returns:
            str: HTML格式的内容
        """
        logger.debug("转换文本为HTML格式")

        # html_lines = [
        #     '<!DOCTYPE html>',
        #     '<html>',
        #     '<head>',
        #     '<meta charset="utf-8">',
        #     '</head>',
        #     f'<body style="margin: 0; padding: 10px; font-family: \'{self._font_family}\'; font-size: {self._font_size}pt;">'
        # ]
        html_lines = []

        paragraphs = self._content.split('\n')
        current_pos = 0  # 用于跟踪文本中字符的绝对位置
        last_empty = False  # 标记上一段是否为空

        for paragraph in paragraphs:
            if not paragraph:
                if last_empty:
                    # 如果连续遇到空行，则仅更新位置，不输出重复的空行
                    current_pos += 1
                    continue
                html_lines.append('<p>&nbsp;</p>')
                last_empty = True
                current_pos += 1  # 空行也占一个换行符位置
                continue

            last_empty = False
            html_lines.append('<p>')

            pos = 0
            while pos < len(paragraph):
                # 获取当前位置所有格式标签，过滤掉 'sel'
                current_tags = {tag for tag in self._tags.get(str(current_pos + pos), []) if tag != 'sel'}

                # 确定连续具有相同格式的区间
                end_pos = pos + 1
                while end_pos < len(paragraph):
                    next_tags = {tag for tag in self._tags.get(str(current_pos + end_pos), []) if tag != 'sel'}
                    if next_tags != current_tags:
                        break
                    end_pos += 1

                # 取出本区间的文本，先进行HTML转义再替换空格
                segment = paragraph[pos:end_pos]
                escaped_text = html.escape(segment)
                escaped_text = escaped_text.replace(' ', '&nbsp;')

                # 根据格式标签构建内联样式
                if current_tags:
                    styles = []
                    if 'bold' in current_tags:
                        styles.append('font-weight: bold')
                    if 'italic' in current_tags:
                        styles.append('font-style: italic')
                    if 'underline' in current_tags:
                        styles.append('text-decoration: underline')
                    for tag in current_tags:
                        if tag.startswith('font-family:'):
                            parts = tag.split(':', 1)
                            if len(parts) == 2:
                                family = parts[1].strip()
                                styles.append(f"font-family: '{family}'")
                        elif tag.startswith('font-size:'):
                            parts = tag.split(':', 1)
                            if len(parts) == 2:
                                size = parts[1].strip()
                                styles.append(f'font-size: {size}pt')
                    style_attr = '; '.join(styles)
                    html_lines.append(f'<span style="{style_attr}">{escaped_text}</span>')
                else:
                    html_lines.append(escaped_text)

                pos = end_pos

            html_lines.append('</p>')
            current_pos += len(paragraph) + 1  # 加上换行符的长度

        # html_lines.append('</body>')
        # html_lines.append('</html>')

        return '\n'.join(html_lines)

    @staticmethod
    def validate_template_params(text: str) -> Set[str]:
        """
        提取模板中的所有参数
        
        从文本中提取所有 {参数名} 格式的参数。
        
        Args:
            text: 模板文本
            
        Returns:
            Set[str]: 参数集合
        """
        pattern = r'\{([^}]+)\}'
        params = set(re.findall(pattern, text))
        logger.debug(f"提取模板参数 - 参数列表: {params}")
        return params

    @staticmethod
    def get_template_params(subject: str, content: str) -> Set[str]:
        """
        获取模板中使用的所有参数
        
        从主题和正文中提取所有使用的参数。
        
        Args:
            subject: 邮件主题
            content: 邮件内容
            
        Returns:
            Set[str]: 参数集合
        """
        logger.debug("获取模板中的所有参数")
        subject_params = TemplateService.validate_template_params(subject)
        content_params = TemplateService.validate_template_params(content)
        all_params = subject_params | content_params
        logger.debug(f"找到的参数: {all_params}")
        return all_params

    @staticmethod
    def validate_template(subject: str, content: str, available_params: Set[str]) -> Tuple[bool, Set[str]]:
        """
        验证模板中的参数是否都已定义
        
        检查模板中使用的参数是否都在可用参数列表中。
        
        Args:
            subject: 邮件主题
            content: 邮件内容
            available_params: 可用参数集合
            
        Returns:
            Tuple[bool, Set[str]]: (是否验证通过, 未定义的参数集合)
        """
        logger.info("验证模板参数")
        # 获取模板中的所有参数
        template_params = TemplateService.get_template_params(subject, content)
        
        # 检查是否有未定义的参数
        undefined_params = template_params - available_params
        
        if undefined_params:
            logger.warning(f"发现未定义的参数: {undefined_params}")
        else:
            logger.debug("模板参数验证通过")
            
        return len(undefined_params) == 0, undefined_params 