"""
邮件群发系统入口模块

作为应用程序的入口点，负责初始化日志系统和启动主窗口。
提供异常捕获和错误处理机制，确保程序能够正常启动和运行。
"""

import sys
import traceback
from src.gui.email_sender_window import EmailSenderWindow
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """
    程序主入口函数
    
    初始化并运行邮件群发系统，包括：
    - 设置全局异常处理
    - 创建并启动主窗口
    - 处理程序退出
    """
    try:
        logger.info("=== 邮件群发系统启动 ===")
        logger.info(f"Python版本: {sys.version}")
        
        # 创建并运行主窗口
        app = EmailSenderWindow()
        logger.info("主窗口创建成功")
        
        # 启动应用程序
        app.run()
        logger.info("=== 邮件群发系统正常退出 ===")
        
    except Exception as e:
        # 记录未捕获的异常
        error_msg = f"程序发生未处理的异常: {str(e)}"
        logger.critical(error_msg, exc_info=True)
        
        # 获取详细的堆栈跟踪
        stack_trace = traceback.format_exc()
        logger.critical(f"堆栈跟踪:\n{stack_trace}")
        
        # 确保错误信息被记录后再退出
        sys.exit(1)

if __name__ == "__main__":
    main() 