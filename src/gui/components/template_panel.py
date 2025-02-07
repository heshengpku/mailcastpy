"""
模板编辑面板模块

提供邮件模板编辑的图形界面组件。
支持HTML/纯文本格式切换、富文本编辑、字体设置等功能。
"""

import tkinter as tk
from tkinter import ttk
from src.utils.font_manager import FontManager
from typing import Optional, Callable, Dict, Any
from src.utils.logger import setup_logger
from src.services.template_service import TemplateService

logger = setup_logger(__name__)

class TemplatePanel(ttk.LabelFrame):
    """
    模板编辑面板类
    
    提供邮件模板编辑功能，包括：
    - 主题和正文编辑
    - HTML/纯文本格式切换
    - 富文本编辑（加粗、斜体、下划线）
    - 字体和字号设置
    
    Attributes:
        font_manager: 字体管理器
        on_content_change: 内容变更的回调函数
        subject: 主题输入框
        content: 正文编辑区
        mail_format: 邮件格式选择
    """
    
    def __init__(self, parent, template_service: TemplateService):
        """
        初始化模板编辑面板
        
        Args:
            parent: 父级窗口组件
            template_service: 模板服务实例
        """
        super().__init__(parent, text="邮件模板设置")
        logger.info("初始化模板编辑面板")
        
        self.template_service = template_service
        self.font_manager = FontManager()
        self.on_content_change: Optional[Callable[[], None]] = None
        self._init_ui()
        
        # 从模板服务加载初始数据
        self._load_template_data()
        logger.debug("模板编辑面板初始化完成")

    def _init_ui(self):
        """
        初始化用户界面
        
        创建主题输入、工具栏和正文编辑区域。
        """
        logger.debug("开始初始化用户界面")
        
        # 主题
        ttk.Label(self, text="主题:").pack(anchor="w", padx=5, pady=5)
        self.subject = ttk.Entry(self)
        self.subject.pack(fill="x", padx=5)
        
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=2)
        
        # 字体选择
        self.font_family = ttk.Combobox(toolbar, width=15)
        self.font_family['values'] = ('Times New Roman', 'Arial', '微软雅黑', '宋体')
        self.font_family.set('Times New Roman')
        self.font_family.pack(side="left", padx=2)
        
        # 字号选择
        self.font_size = ttk.Combobox(toolbar, width=5)
        self.font_size['values'] = ('10', '12', '14', '16', '18', '20')
        self.font_size.set('12')
        self.font_size.pack(side="left", padx=2)
        
        # 格式按钮
        self.bold_btn = ttk.Button(toolbar, text="B", width=3, command=self.toggle_bold)
        self.bold_btn.pack(side="left", padx=2)
        
        self.italic_btn = ttk.Button(toolbar, text="I", width=3, command=self.toggle_italic)
        self.italic_btn.pack(side="left", padx=2)
        
        self.underline_btn = ttk.Button(toolbar, text="U", width=3, command=self.toggle_underline)
        self.underline_btn.pack(side="left", padx=2)
        
        # 邮件格式选择
        self.mail_format = tk.StringVar(value="html")
        ttk.Radiobutton(toolbar, text="HTML", variable=self.mail_format, 
                       value="html", command=self._on_format_change).pack(side="right", padx=5)
        ttk.Radiobutton(toolbar, text="纯文本", variable=self.mail_format, 
                       value="plain", command=self._on_format_change).pack(side="right", padx=5)
        
        # 内容编辑区
        self.content = tk.Text(self, height=10, undo=True)
        self.content.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 绑定字体更改事件
        self.font_family.bind('<<ComboboxSelected>>', self.apply_font)
        self.font_size.bind('<<ComboboxSelected>>', self.apply_font)
        
        # 设置默认字体
        self.content.configure(font=self.font_manager.current_font)
        
        # 绑定内容变更事件
        self.subject.bind('<KeyRelease>', lambda e: self._notify_content_change())
        self.content.bind('<KeyRelease>', lambda e: self._notify_content_change())
        
        logger.debug("用户界面初始化完成")

    def toggle_bold(self):
        """切换选中文本的加粗状态"""
        try:
            current_tags = self.content.tag_names("sel.first")
            if "bold" in current_tags:
                logger.debug("移除加粗格式")
                self.content.tag_remove("bold", "sel.first", "sel.last")
            else:
                logger.debug("添加加粗格式")
                self.content.tag_add("bold", "sel.first", "sel.last")
                # 创建加粗字体并应用
                current_font = self.content.cget("font")
                if isinstance(current_font, str):
                    current_font = self.font_manager.current_font
                bold_font = self.font_manager.create_font(
                    family=current_font.cget("family"),
                    size=current_font.cget("size"),
                    weight="bold"
                )
                self.content.tag_configure("bold", font=bold_font)
            self._notify_content_change()
        except tk.TclError:
            logger.debug("未选中文本，忽略加粗操作")
            pass

    def toggle_italic(self):
        """切换选中文本的斜体状态"""
        try:
            current_tags = self.content.tag_names("sel.first")
            if "italic" in current_tags:
                logger.debug("移除斜体格式")
                self.content.tag_remove("italic", "sel.first", "sel.last")
            else:
                logger.debug("添加斜体格式")
                self.content.tag_add("italic", "sel.first", "sel.last")
                # 创建斜体字体并应用
                current_font = self.content.cget("font")
                if isinstance(current_font, str):
                    current_font = self.font_manager.current_font
                italic_font = self.font_manager.create_font(
                    family=current_font.cget("family"),
                    size=current_font.cget("size"),
                    slant="italic"
                )
                self.content.tag_configure("italic", font=italic_font)
            self._notify_content_change()
        except tk.TclError:
            logger.debug("未选中文本，忽略斜体操作")
            pass

    def toggle_underline(self):
        """切换选中文本的下划线状态"""
        try:
            current_tags = self.content.tag_names("sel.first")
            if "underline" in current_tags:
                logger.debug("移除下划线格式")
                self.content.tag_remove("underline", "sel.first", "sel.last")
            else:
                logger.debug("添加下划线格式")
                self.content.tag_add("underline", "sel.first", "sel.last")
                underline_font = self.font_manager.create_font(underline=True)
                self.content.tag_configure("underline", font=underline_font)
            self._notify_content_change()
        except tk.TclError:
            logger.debug("未选中文本，忽略下划线操作")
            pass

    def apply_font(self, event=None):
        """
        应用字体到选中的文本
        
        Args:
            event: 事件对象（可选）
        """
        try:
            # 获取选中的文本范围
            try:
                selected_range = self.content.tag_ranges("sel")
                if selected_range:
                    # 如果有选中文本，只应用到选中部分
                    tag_name = f"font_{self.font_family.get()}_{self.font_size.get()}"
                    self.content.tag_add(tag_name, "sel.first", "sel.last")
                    new_font = self.font_manager.create_font(
                        family=self.font_family.get(),
                        size=int(self.font_size.get())
                    )
                    self.content.tag_configure(tag_name, font=new_font)
                else:
                    # 如果没有选中文本，应用到整个文本框
                    new_font = self.font_manager.create_font(
                        family=self.font_family.get(),
                        size=int(self.font_size.get())
                    )
                    self.content.configure(font=new_font)
            except tk.TclError:
                # 如果没有选中文本，应用到整个文本框
                new_font = self.font_manager.create_font(
                    family=self.font_family.get(),
                    size=int(self.font_size.get())
                )
                self.content.configure(font=new_font)
                
            logger.debug(f"应用字体 - 字体: {self.font_family.get()}, 字号: {self.font_size.get()}")
            self._notify_content_change()
            
        except Exception as e:
            error_msg = f"设置字体失败: {str(e)}"
            logger.error(error_msg, exc_info=True)

    def get_template_config(self) -> Dict[str, Any]:
        """
        获取当前模板配置

        提取文本内容和格式标签，将 Tkinter 富文本转换为适合 HTML 渲染的格式。
        该方法通过逐字符遍历文本内容，从而精确记录各个字符的位置所对应的格式标签，
        确保在标签范围、标签合并与换行符处理上与实际设置保持一致。

        Returns:
            Dict[str, Any]: 包含模板配置的字典，其中包括:
                - subject: 邮件主题
                - content: 文本内容
                - is_html: 是否为HTML格式
                - tags: 根据绝对字符位置映射的标签字典
                - font_family: 字体族
                - font_size: 字号
        """
        logger.debug("获取模板配置")

        # 获取所有文本内容
        content = self.content.get("1.0", "end-1c")
        tags = {}

        # 遍历文本中每个字符的位置，并记录每个字符的激活标签
        for i in range(len(content)):
            # 将绝对位置 i 转换为 Tkinter 索引（例如："1.0+{i}c"）
            tk_index = self.content.index(f"1.0+{i}c")
            current_tags = self.content.tag_names(tk_index)
            if current_tags:
                tags[str(i)] = list(current_tags)

        return {
            "subject": self.subject.get(),
            "content": content,
            "is_html": self.mail_format.get() == "html",
            "tags": tags,
            "font_family": self.font_family.get(),
            "font_size": self.font_size.get()
        }

    def set_content_change_callback(self, callback: Callable[[], None]):
        """
        设置内容变更回调函数
        
        Args:
            callback: 内容变更时的回调函数
        """
        self.on_content_change = callback

    def _load_template_data(self):
        """从模板服务加载数据"""
        logger.debug("从模板服务加载数据")
        template_data = self.template_service.get_template()
        
        # 设置主题
        self.subject.delete(0, tk.END)
        self.subject.insert(0, template_data['subject'])
        
        # 设置内容
        self.content.delete("1.0", tk.END)
        self.content.insert("1.0", template_data['content'])
        
        # 设置格式
        self.mail_format.set("html" if template_data['is_html'] else "plain")
        
        # 设置字体和字号
        self.font_family.set(template_data['font_family'])
        self.font_size.set(template_data['font_size'])
        
        # 应用格式标签
        for pos, tags in template_data['tags'].items():
            for tag in tags:
                if tag in ["bold", "italic", "underline"]:
                    self.content.tag_add(tag, f"1.{pos}")

    def _notify_content_change(self):
        """通知内容变化"""
        try:
            # 更新模板服务中的数据
            template_config = self.get_template_config()
            self.template_service.update_template(
                subject=template_config['subject'],
                content=template_config['content'],
                is_html=template_config['is_html'],
                tags=template_config['tags'],
                font_family=template_config['font_family'],
                font_size=template_config['font_size']
            )
            
            # 调用回调函数
            if self.on_content_change:
                logger.debug("通知内容变更")
                self.on_content_change()
        except Exception as e:
            error_msg = f"通知内容变化时出错: {str(e)}"
            logger.error(error_msg, exc_info=True)

    def _on_format_change(self):
        """处理邮件格式变更事件"""
        is_html = self.mail_format.get() == "html"
        # 更新按钮状态
        self.bold_btn.configure(state="normal" if is_html else "disabled")
        self.italic_btn.configure(state="normal" if is_html else "disabled")
        self.underline_btn.configure(state="normal" if is_html else "disabled")
        self.font_family.configure(state="normal" if is_html else "disabled")
        self.font_size.configure(state="normal" if is_html else "disabled")
        # 通知内容变更
        self._notify_content_change() 