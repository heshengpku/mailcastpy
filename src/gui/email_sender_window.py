"""
邮件发送主窗口模块

提供邮件群发系统的主界面，集成了服务器设置、模板编辑、
参数管理和收件人列表等功能面板。负责协调各个组件的交互和
邮件发送流程的控制。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from src.gui.components.parameter_panel import ParameterPanel
from src.gui.components.server_panel import ServerPanel
from src.gui.components.template_panel import TemplatePanel
from src.gui.components.recipients_panel import RecipientsPanel
from src.services.email_service import EmailService
from src.services.template_service import TemplateService
from src.services.parameter_service import ParameterService
from typing import List, Set, Dict
from src.utils.logger import setup_logger
from src.gui.components.preview_window import PreviewWindow

logger = setup_logger(__name__)

class EmailSenderWindow:
    """
    邮件发送主窗口类
    
    提供邮件群发系统的主界面，包括：
    - 参数设置面板
    - 服务器配置面板
    - 模板编辑面板
    - 收件人列表面板
    - 邮件发送控制
    
    负责协调各个组件之间的交互，处理用户操作，
    并控制邮件发送流程。
    """
    
    def __init__(self):
        """初始化主窗口"""
        logger.info("初始化邮件发送主窗口")
        self.window = tk.Tk()
        self.window.title("邮件群发系统")
        
        # 创建服务实例
        self.template_service = TemplateService()
        
        # 获取屏幕尺寸
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        
        # 计算窗口大小（屏幕的80%）
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # 计算窗口位置（居中）
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self._init_ui()
        logger.debug("主窗口初始化完成")

    def _init_ui(self):
        """
        初始化用户界面
        
        创建并布局主要的界面组件，包括：
        - 左侧参数设置面板
        - 中间的服务器配置和模板编辑面板
        - 右侧的收件人列表面板
        - 底部的操作按钮
        """
        logger.debug("开始初始化用户界面")
        
        # 创建主内容区域（三列布局）
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 左侧面板（参数设置）- 设置固定宽度
        left_frame = ttk.Frame(main_frame, width=250)
        left_frame.pack(side="left", fill="y", padx=(0,5))
        left_frame.pack_propagate(False)
        
        # 参数设置面板
        self.param_panel = ParameterPanel(left_frame)
        self.param_panel.pack(fill="both", expand=True)
        
        # 设置参数变更回调
        self.param_panel.set_params_change_callback(self.on_params_change)
        
        # 中间面板
        middle_frame = ttk.Frame(main_frame)
        middle_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        # 服务器设置面板
        self.server_panel = ServerPanel(middle_frame)
        self.server_panel.pack(fill="x", pady=(0,5))
        
        # 模板设置面板
        self.template_panel = TemplatePanel(middle_frame, self.template_service)
        self.template_panel.pack(fill="both", expand=True, pady=5)
        
        # 设置模板内容变更回调
        self.template_panel.set_content_change_callback(self.on_template_change)
        
        # 按钮区域
        btn_frame = ttk.Frame(middle_frame)
        btn_frame.pack(pady=10)
        
        # 预览按钮
        self.preview_btn = ttk.Button(btn_frame, text="预览邮件", command=self.preview_emails)
        self.preview_btn.pack(side="left", padx=5)
        
        # 验证按钮
        self.validate_btn = ttk.Button(btn_frame, text="发送前校验", command=self.validate)
        self.validate_btn.pack(side="left", padx=5)
        
        # 发送按钮
        self.send_btn = ttk.Button(btn_frame, text="发送邮件", command=self.send_emails)
        self.send_btn.pack(side="left", padx=5)
        
        # 右侧面板（收件人列表）
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side="left", fill="both", expand=True, padx=(5,0))
        
        # 收件人列表面板
        self.recipients_panel = RecipientsPanel(right_frame)
        self.recipients_panel.pack(fill="both", expand=True)
        
        # 设置收件人列表导入回调
        self.recipients_panel.set_import_callback(self.on_recipients_imported)
        
        logger.debug("用户界面初始化完成")

    def on_params_change(self, custom_params: List[str], display_names: Dict[str, str]):
        """
        处理参数变更事件
        
        当参数设置发生变化时，更新相关组件的显示和状态。
        
        Args:
            custom_params: 自定义参数标识符列表
            display_names: 所有参数的显示名称映射
        """
        logger.info("处理参数变更事件")
        # 获取所有可用参数（包括基本参数和自定义参数）
        available_params = ParameterService.merge_params(custom_params)
        
        # 更新收件人列表的模板参数和列显示
        self.recipients_panel.sync_custom_params(custom_params)
        
        # 检查模板参数
        self.check_template_params(available_params)
        logger.debug("参数变更处理完成")

    def on_template_change(self):
        """
        处理模板内容变更事件
        
        当模板内容发生变化时，更新模板服务中的数据。
        """
        logger.debug("处理模板内容变更事件")
        
        # 获取模板面板的当前配置
        template_config = self.template_panel.get_template_config()
        
        # 更新模板服务中的数据
        self.template_service.update_template(
            subject=template_config['subject'],
            content=template_config['content'],
            is_html=template_config['is_html'],
            tags=template_config['tags'],
            font_family=template_config['font_family'],
            font_size=template_config['font_size']
        )

    def check_template_params(self, available_params: Set[str]):
        """
        检查模板参数是否都已定义
        
        Args:
            available_params: 当前可用的参数集合
        """
        logger.debug("检查模板参数")
        # 获取模板中使用的参数
        template_config = self.template_panel.get_template_config()
        template_params = TemplateService.get_template_params(
            template_config['subject'],
            template_config['content']
        )

        # 检查是否有未定义的参数
        undefined_params = template_params - available_params
        if undefined_params:
            logger.warning(f"发现未定义的模板参数: {undefined_params}")
            messagebox.showwarning("参数未定义",
                f"模板中使用了未定义的参数：\n{', '.join(undefined_params)}\n"
                "请在参数设置中添加这些参数。")

    def validate(self) -> bool:
        """
        验证配置和模板
        
        验证SMTP服务器连接和模板参数的有效性。
        
        Returns:
            bool: 验证是否通过
        """
        logger.info("开始验证配置和模板")
        # 1. 验证服务器配置
        try:
            server_config = self.server_panel.get_server_config()
            email_service = EmailService(**server_config)
            success, message = email_service.test_connection()
            if not success:
                logger.error(f"服务器连接失败: {message}")
                messagebox.showerror("服务器连接失败", f"无法连接到SMTP服务器：\n{message}")
                return False
        except Exception as e:
            error_msg = f"服务器配置错误: {str(e)}"
            logger.error(error_msg)
            messagebox.showerror("服务器配置错误", error_msg)
            return False
            
        # 2. 获取所有可用参数
        available_params = ParameterService.merge_params(
            ParameterService.get_custom_param_identifiers())
            
        # 3. 验证模板参数
        template_config = self.template_panel.get_template_config()
        is_valid, undefined_params = TemplateService.validate_template(
            template_config['subject'],
            template_config['content'],
            available_params
        )
        
        if not is_valid:
            error_msg = f"以下参数未定义：\n{', '.join(undefined_params)}\n\n请在参数设置中添加这些参数。"
            logger.error(f"模板参数验证失败: {error_msg}")
            messagebox.showerror("模板参数错误", error_msg)
            return False
            
        logger.info("配置和模板验证通过")
        messagebox.showinfo("验证成功", 
            "✓ SMTP服务器连接正常\n"
            "✓ 模板参数验证通过")
        return True

    def send_emails(self):
        """
        发送邮件
        
        执行邮件发送流程，包括：
        - 验证配置和模板
        - 获取收件人列表
        - 逐个发送邮件
        - 更新发送状态
        """
        logger.info("开始发送邮件")
        # 首先进行验证
        if not self.validate():
            return
            
        recipients = self.recipients_panel.get_recipients()
        if not recipients:
            logger.warning("收件人列表为空")
            messagebox.showerror("错误", "请先导入收件人列表")
            return
            
        try:
            # 获取服务器配置
            server_config = self.server_panel.get_server_config()
            
            # 获取模板配置
            template_config = self.template_service.get_template()
            
            # 创建邮件服务
            with EmailService(**server_config) as email_service:
                for recipient in recipients:
                    try:
                        # 更新状态为"发送中"
                        self.recipients_panel.update_status(recipient['email'], "发送中")
                        self.window.update()
                        
                        # 替换模板变量
                        subject = TemplateService.replace_variables(template_config['subject'], recipient)
                        content = TemplateService.replace_variables(template_config['content'], recipient)
                        
                        # 如果是HTML格式，转换内容
                        if template_config['is_html']:
                            content = TemplateService.replace_variables(self.template_service.get_html_content(), recipient)
                        
                        # 发送邮件
                        logger.debug(f"发送邮件到: {recipient['email']}")
                        success = email_service.send_email(
                            to_email=recipient['email'],
                            subject=subject,
                            content=content,
                            is_html=template_config['is_html']
                        )
                        
                        # 更新状态
                        status = "已发送" if success else "发送失败"
                        self.recipients_panel.update_status(recipient['email'], status)
                        
                    except Exception as e:
                        error_msg = f"发送给 {recipient['email']} 失败: {str(e)}"
                        logger.error(error_msg)
                        self.recipients_panel.update_status(recipient['email'], "发送失败")
                    
                    self.window.update()
            
            logger.info("邮件发送完成")
            messagebox.showinfo("成功", "邮件发送完成")
            
        except Exception as e:
            error_msg = f"发送失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("错误", error_msg)

    def on_recipients_imported(self, success: bool):
        """
        处理收件人列表导入事件
        
        Args:
            success: 是否成功导入CSV文件。如果为False，表示清空了列表或导入失败
        """
        logger.debug(f"处理收件人导入事件 - 成功: {success}")
        if success:
            # 禁用参数编辑
            self.param_panel.disable_editing()
            logger.debug("禁用参数编辑功能")
        else:
            # 如果是清空列表或导入失败，启用参数编辑
            self.param_panel.enable_editing()
            logger.debug("启用参数编辑功能")

    def preview_emails(self):
        """
        预览邮件
        
        显示前10个收件人（或实际数量）的邮件预览，包括：
        - 替换后的邮件主题
        - 替换后的邮件内容
        - HTML格式显示
        - 翻页功能
        """
        logger.info("开始预览邮件")
        
        # 获取收件人列表
        recipients = self.recipients_panel.get_recipients()
        if not recipients:
            logger.warning("收件人列表为空")
            messagebox.showerror("错误", "请先导入收件人列表")
            return
        
        # 获取前10个收件人（或实际数量）
        preview_data = recipients[:min(10, len(recipients))]
        
        try:
            # 创建预览窗口
            preview_window = PreviewWindow(
                self.window,
                preview_data=preview_data,
                template_service=self.template_service
            )
            
            # 设置模态窗口
            preview_window.transient(self.window)
            preview_window.grab_set()
            
            logger.debug(f"显示邮件预览窗口，预览数量: {len(preview_data)}")
            
        except Exception as e:
            error_msg = f"创建预览窗口失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("错误", error_msg)

    def run(self):
        """运行程序"""
        logger.info("启动邮件群发系统")
        self.window.mainloop() 