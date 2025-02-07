"""
服务器设置面板模块

提供SMTP服务器配置的图形界面组件。
支持服务器地址、端口、发件人邮箱和密码的设置。
"""

import tkinter as tk
from tkinter import ttk
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ServerPanel(ttk.LabelFrame):
    """
    服务器设置面板类
    
    提供SMTP服务器配置的界面，包括：
    - 服务器地址和端口设置
    - 发件人邮箱和密码设置
    - 配置信息的获取
    
    Attributes:
        smtp_server: SMTP服务器地址输入框
        smtp_port: SMTP服务器端口输入框
        sender_email: 发件人邮箱输入框
        sender_password: 发件人密码输入框
    """
    
    def __init__(self, parent):
        """
        初始化服务器设置面板
        
        Args:
            parent: 父级窗口组件
        """
        super().__init__(parent, text="邮件服务器设置")
        logger.info("初始化服务器设置面板")
        self._init_ui()
        logger.debug("服务器设置面板初始化完成")

    def _init_ui(self):
        """
        初始化用户界面
        
        创建服务器配置相关的输入框和标签。
        """
        logger.debug("开始初始化用户界面")
        
        # SMTP服务器设置
        ttk.Label(self, text="SMTP服务器:").grid(row=0, column=0, padx=5, pady=5)
        self.smtp_server = ttk.Entry(self)
        self.smtp_server.insert(0, "smtp.163.com")
        self.smtp_server.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="端口:").grid(row=0, column=2, padx=5, pady=5)
        self.smtp_port = ttk.Entry(self)
        self.smtp_port.insert(0, "25")
        self.smtp_port.grid(row=0, column=3, padx=5, pady=5)
        
        # 发件人设置
        ttk.Label(self, text="发件人邮箱:").grid(row=1, column=0, padx=5, pady=5)
        self.sender_email = ttk.Entry(self)
        self.sender_email.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self, text="密码:").grid(row=1, column=2, padx=5, pady=5)
        self.sender_password = ttk.Entry(self, show="*")
        self.sender_password.grid(row=1, column=3, padx=5, pady=5)
        
        logger.debug("用户界面初始化完成")

    def get_server_config(self) -> dict:
        """
        获取服务器配置
        
        Returns:
            dict: 包含服务器配置的字典，包括：
                - smtp_server: SMTP服务器地址
                - smtp_port: SMTP服务器端口
                - sender_email: 发件人邮箱
                - sender_password: 发件人密码
        """
        config = {
            'smtp_server': self.smtp_server.get(),
            'smtp_port': int(self.smtp_port.get()),
            'sender_email': self.sender_email.get(),
            'sender_password': self.sender_password.get()
        }
        logger.debug(f"获取服务器配置 - 服务器: {config['smtp_server']}:{config['smtp_port']}")
        return config