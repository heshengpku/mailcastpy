"""
邮件预览窗口模块

提供邮件发送前的预览功能，支持查看替换参数后的邮件效果。
包括标题和内容的预览，支持HTML格式显示，提供翻页功能。
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict
from tkhtmlview import HTMLScrolledText
from src.services.template_service import TemplateService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class PreviewWindow(tk.Toplevel):
    """
    邮件预览窗口类
    
    提供邮件预览功能，包括：
    - 邮件标题和内容预览
    - HTML格式显示和渲染（仅HTML模式）
    - HTML源码查看（仅HTML模式）
    - 翻页功能
    - 预览数量控制
    
    Attributes:
        current_page: 当前页码
        total_pages: 总页数
        preview_data: 预览数据列表
        template_service: 模板服务实例
        is_html_view: 是否为HTML渲染视图（仅HTML模式）
        current_html: 当前的HTML内容（仅HTML模式）
    """
    
    def __init__(self, parent, preview_data: List[Dict[str, str]], 
                 template_service: TemplateService):
        """
        初始化预览窗口
        
        Args:
            parent: 父级窗口
            preview_data: 预览数据列表
            template_service: 模板服务实例
        """
        super().__init__(parent)
        logger.info("初始化邮件预览窗口")
        
        self.title("邮件预览")
        self.preview_data = preview_data
        self.template_service = template_service
        
        # 获取模板格式
        template_data = template_service.get_template()
        self.is_html = template_data['is_html']
        
        # 仅在HTML模式下初始化相关属性
        if self.is_html:
            self.is_html_view = True  # 默认显示HTML渲染视图
            self.current_html = ""    # 存储当前的HTML内容
        
        self.current_page = 0
        self.total_pages = len(preview_data)
        
        # 设置窗口大小和位置
        window_width = 800
        window_height = 600
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self._init_ui()
        self.update_preview()
        logger.debug("预览窗口初始化完成")

    def _init_ui(self):
        """初始化用户界面"""
        logger.debug("开始初始化预览窗口界面")
        
        # 主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # 收件人信息
        recipient_frame = ttk.Frame(main_frame)
        recipient_frame.pack(fill="x", pady=(0, 5))
        self.recipient_label = ttk.Label(recipient_frame, text="")
        self.recipient_label.pack(side="left")
        
        # 标题区域
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(title_frame, text="主题: ").pack(side="left")
        self.subject_label = ttk.Label(title_frame, wraplength=700)
        self.subject_label.pack(side="left", fill="x", expand=True)
        
        # 内容区域
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # 根据模板格式创建不同的视图
        template_data = self.template_service.get_template()
        self.is_html = template_data['is_html']
        
        if self.is_html:
            # HTML模式：创建渲染视图和源码视图
            self.html_view = HTMLScrolledText(content_frame)
            self.source_view = tk.Text(content_frame, wrap="word", padx=5, pady=5)
            scrollbar = ttk.Scrollbar(content_frame, orient="vertical", 
                                    command=self.source_view.yview)
            self.source_view.configure(yscrollcommand=scrollbar.set)
            
            # 默认显示HTML渲染视图
            self.html_view.pack(fill="both", expand=True)
            # 设置只读
            self.html_view.configure(state="disabled")
        else:
            # 纯文本模式：创建只读文本视图
            self.text_view = tk.Text(content_frame, wrap="word", padx=5, pady=5)
            scrollbar = ttk.Scrollbar(content_frame, orient="vertical", 
                                    command=self.text_view.yview)
            self.text_view.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side="right", fill="y")
            self.text_view.pack(side="left", fill="both", expand=True)
            # 设置只读
            self.text_view.configure(state="disabled")
        
        # 导航区域
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill="x", pady=(10, 0))
        
        # 页码信息
        self.page_label = ttk.Label(nav_frame, text="")
        self.page_label.pack(side="left", padx=20)
        
        # 导航按钮
        btn_frame = ttk.Frame(nav_frame)
        btn_frame.pack(side="right")
        
        # 创建导航按钮
        self.prev_btn = ttk.Button(btn_frame, text="上一页", command=self.prev_page)
        self.prev_btn.pack(side="left", padx=5)
        
        self.next_btn = ttk.Button(btn_frame, text="下一页", command=self.next_page)
        self.next_btn.pack(side="left", padx=5)
        
        # 只在HTML模式下添加视图切换按钮
        if self.is_html:
            self.view_btn = ttk.Button(btn_frame, text="查看HTML源码", 
                                     command=self.toggle_view)
            self.view_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="关闭", command=self.destroy).pack(side="left", padx=5)
        
        logger.debug("预览窗口界面初始化完成")

    def toggle_view(self):
        """切换HTML渲染视图和源码视图（仅HTML模式）"""
        if not self.is_html:
            return
            
        logger.debug(f"切换视图模式 - 当前模式: {'HTML渲染' if self.is_html_view else 'HTML源码'}")
        
        if self.is_html_view:
            # 切换到源码视图
            self.html_view.pack_forget()
            self.source_view.pack(side="left", fill="both", expand=True)
            self.source_view.configure(state="normal")
            self.source_view.delete("1.0", tk.END)
            self.source_view.insert("1.0", self.current_html)
            self.source_view.configure(state="disabled")
            self.view_btn.configure(text="查看渲染效果")
        else:
            # 切换回HTML渲染视图
            self.source_view.pack_forget()
            self.html_view.pack(fill="both", expand=True)
            self.view_btn.configure(text="查看HTML源码")
        
        self.is_html_view = not self.is_html_view

    def update_preview(self):
        """更新预览内容，并校验参数"""
        logger.debug(f"更新预览内容 - 当前页: {self.current_page + 1}")
        
        try:
            # 获取当前收件人数据
            recipient = self.preview_data[self.current_page]
            
            # 获取模板数据
            template_data = self.template_service.get_template()
            
            # 校验参数
            missing_params = self._validate_params(template_data, recipient)
            if missing_params:
                error_msg = f"以下参数未定义: {', '.join(missing_params)}"
                logger.warning(f"参数校验失败: {error_msg}")
                tk.messagebox.showwarning("参数校验", error_msg)
            
            # 替换变量
            subject = TemplateService.replace_variables(template_data['subject'], recipient)
            content = TemplateService.replace_variables(template_data['content'], recipient)
            
            if template_data['is_html']:
                # HTML模式：更新当前HTML内容
                self.current_html = TemplateService.replace_variables(self.template_service.get_html_content(), recipient)
                # 更新当前显示的视图
                if self.is_html_view:
                    self.html_view.configure(state="normal")

                    self.html_view.set_html(self.current_html)
                    self.html_view.configure(state="disabled")
                else:
                    self.source_view.configure(state="normal")
                    self.source_view.delete("1.0", tk.END)
                    self.source_view.insert("1.0", self.current_html)
                    self.source_view.configure(state="disabled")
            else:
                # 纯文本模式：直接显示替换变量后的内容
                self.text_view.configure(state="normal")  # 临时启用编辑
                self.text_view.delete("1.0", tk.END)
                self.text_view.insert("1.0", content)
                self.text_view.configure(state="disabled")  # 恢复只读
            
            # 更新显示
            self.subject_label.configure(text=subject)
            
            # 更新收件人和页码信息
            self.recipient_label.configure(
                text=f"收件人: {recipient.get('name', '')} ({recipient.get('email', '')})"
            )
            self.page_label.configure(
                text=f"第 {self.current_page + 1} 页，共 {self.total_pages} 页"
            )
            
            # 更新按钮状态
            self.prev_btn.configure(state="normal" if self.current_page > 0 else "disabled")
            self.next_btn.configure(
                state="normal" if self.current_page < self.total_pages - 1 else "disabled"
            )
            
        except Exception as e:
            logger.error(f"更新预览内容时出错: {str(e)}", exc_info=True)
            tk.messagebox.showerror("错误", f"更新预览内容时出错: {str(e)}")

    def _validate_params(self, template_data: Dict, recipient: Dict) -> List[str]:
        """
        校验模板中使用的参数是否都已定义
        
        Args:
            template_data: 模板数据
            recipient: 收件人数据
            
        Returns:
            List[str]: 未定义的参数列表
        """
        # 从模板中提取所有参数
        template_params = TemplateService.get_template_params(
            template_data['subject'],
            template_data['content']
        )
        
        # 检查每个参数是否在收件人数据中定义
        missing_params = []
        for param in template_params:
            if param not in recipient:
                missing_params.append(param)
        
        return missing_params

    def prev_page(self):
        """显示上一页"""
        if self.current_page > 0:
            logger.debug("切换到上一页")
            self.current_page -= 1
            self.update_preview()

    def next_page(self):
        """显示下一页"""
        if self.current_page < self.total_pages - 1:
            logger.debug("切换到下一页")
            self.current_page += 1
            self.update_preview() 