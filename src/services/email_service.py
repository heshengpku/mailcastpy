"""
邮件发送服务模块

提供SMTP邮件发送功能，支持HTML和纯文本格式，
包括服务器连接管理、邮件发送和错误处理。
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Tuple
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class EmailService:
    """
    邮件发送服务类
    
    提供邮件发送相关功能，包括：
    - SMTP服务器连接管理
    - 邮件发送
    - 连接测试
    
    Attributes:
        smtp_server: SMTP服务器地址
        smtp_port: SMTP服务器端口
        sender_email: 发件人邮箱
        sender_password: 发件人密码
        _server: SMTP服务器连接对象
    """
    
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        """
        初始化邮件服务
        
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP服务器端口
            sender_email: 发件人邮箱
            sender_password: 发件人密码
        """
        logger.info(f"初始化邮件服务 - 服务器: {smtp_server}:{smtp_port}")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self._server: Optional[smtplib.SMTP] = None

    def connect(self):
        """
        连接到SMTP服务器
        
        建立与SMTP服务器的连接，并进行身份验证。
        """
        logger.info(f"连接SMTP服务器 - {self.smtp_server}:{self.smtp_port}")
        try:
            self._server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            self._server.starttls()
            self._server.login(self.sender_email, self.sender_password)
            logger.debug("SMTP服务器连接成功")
        except Exception as e:
            error_msg = f"连接SMTP服务器失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise

    def disconnect(self):
        """断开SMTP服务器连接"""
        if self._server:
            try:
                self._server.quit()
                logger.debug("SMTP服务器连接已断开")
            except Exception as e:
                logger.warning(f"断开SMTP服务器连接时出错: {str(e)}")
            finally:
                self._server = None

    def test_connection(self) -> Tuple[bool, str]:
        """
        测试SMTP服务器连接
        
        Returns:
            Tuple[bool, str]: (是否连接成功, 错误信息)
        """
        logger.info("测试SMTP服务器连接")
        try:
            self.connect()
            self.disconnect()
            logger.info("SMTP服务器连接测试成功")
            return True, "连接成功"
        except Exception as e:
            error_msg = str(e)
            logger.error(f"SMTP服务器连接测试失败: {error_msg}")
            return False, error_msg

    def send_email(self, to_email: str, subject: str, content: str, is_html: bool = False) -> bool:
        """
        发送单封邮件
        
        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            content: 邮件内容
            is_html: 是否为HTML格式
            
        Returns:
            bool: 发送是否成功
        """
        try:
            logger.info(f"发送邮件 - 收件人: {to_email}")
            
            if not self._server:
                self.connect()

            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            content_type = 'html' if is_html else 'plain'
            msg.attach(MIMEText(content, content_type, 'utf-8'))

            self._server.send_message(msg)
            logger.debug("邮件发送成功")
            return True
            
        except Exception as e:
            error_msg = f"发送邮件失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.disconnect() 