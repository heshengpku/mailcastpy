"""
参数设置面板模块

提供参数的添加、删除和管理功能的图形界面组件。
支持默认参数显示和自定义参数的添加、删除操作。
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Tuple, Callable, Optional, Dict
from src.services.parameter_service import ParameterService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ParameterPanel(ttk.LabelFrame):
    """
    参数设置面板类
    
    提供参数管理的图形界面，包括：
    - 显示默认参数（姓名、邮箱）
    - 添加自定义参数
    - 删除自定义参数
    - 参数编辑状态管理
    
    Attributes:
        on_params_change: 参数变更的回调函数
        param_frames: 参数行的Frame字典
    """
    
    def __init__(self, parent):
        """
        初始化参数设置面板
        
        Args:
            parent: 父级窗口组件
        """
        super().__init__(parent, text="参数设置")
        logger.info("初始化参数设置面板")
        
        self.on_params_change: Optional[Callable[[List[str], Dict[str, str]], None]] = None
        self.param_frames: Dict[str, ttk.Frame] = {}  # 存储参数行的Frame
        self._init_ui()
        logger.debug("参数设置面板初始化完成")

    def _init_ui(self):
        """
        初始化用户界面
        
        创建默认参数显示区域和自定义参数管理区域。
        """
        logger.debug("开始初始化用户界面")
        
        # 默认参数显示
        ttk.Label(self, text="默认参数：").pack(anchor="w", padx=5, pady=2)
        default_params = ParameterService.get_default_params()
        for param_id, display_name in default_params.items():
            param_text = f"{display_name}: {{{param_id}}}"
            ttk.Label(self, text=param_text).pack(anchor="w", padx=20, pady=2)
        
        # 自定义参数列表
        ttk.Label(self, text="自定义参数：").pack(anchor="w", padx=5, pady=2)
        
        # 创建一个框架来容纳自定义参数和添加按钮
        self.params_container = ttk.Frame(self)
        self.params_container.pack(fill="x", padx=5)
        
        # 自定义参数的框架
        self.custom_params_frame = ttk.Frame(self.params_container)
        self.custom_params_frame.pack(fill="x", pady=5)
        
        # 添加参数按钮
        self.add_param_btn = ttk.Button(self.params_container, text="添加参数", command=self.add_param)
        self.add_param_btn.pack(pady=5)
        
        # 恢复已有的自定义参数
        self._restore_custom_params()
        logger.debug("用户界面初始化完成")

    def _restore_custom_params(self):
        """恢复已有的自定义参数显示"""
        logger.debug("开始恢复自定义参数显示")
        for display_name, identifier in ParameterService.get_custom_params():
            self._create_param_row(display_name, identifier)
        logger.debug("自定义参数显示恢复完成")

    def _create_param_row(self, display_name: str, identifier: str) -> ttk.Frame:
        """
        创建参数行
        
        Args:
            display_name: 显示名称
            identifier: 参数标识符
            
        Returns:
            ttk.Frame: 参数行的Frame
        """
        logger.debug(f"创建参数行 - 显示名称: {display_name}, 标识符: {identifier}")
        
        # 创建参数行
        row_frame = ttk.Frame(self.custom_params_frame)
        row_frame.pack(fill="x", pady=2)
        
        # 显示参数信息
        param_text = f"{display_name}: {{{identifier}}}"
        ttk.Label(row_frame, text=param_text).pack(side="left", padx=2)
        
        def remove_param():
            """移除参数"""
            logger.info(f"移除参数 - 标识符: {identifier}")
            if ParameterService.remove_param(identifier):
                row_frame.destroy()
                del self.param_frames[identifier]
                # 如果是最后一个参数被删除，重新调整custom_params_frame的大小
                if not self.param_frames:
                    self.custom_params_frame.pack_forget()
                    self.custom_params_frame.pack(fill="x", pady=5)
                self._notify_params_change()
                logger.debug("参数移除成功")
        
        # 添加删除按钮
        remove_btn = ttk.Button(row_frame, text="×", width=3, command=remove_param)
        remove_btn.pack(side="right", padx=2)
        
        # 保存Frame引用
        self.param_frames[identifier] = row_frame
        
        return row_frame

    def save_param(self, name: str, identifier: str, dialog: tk.Toplevel) -> bool:
        """
        保存参数
        
        Args:
            name: 显示名称
            identifier: 参数标识符
            dialog: 弹窗对象
            
        Returns:
            bool: 是否保存成功
        """
        try:
            logger.info(f"保存参数 - 显示名称: {name}, 标识符: {identifier}")
            
            # 添加参数
            success, error_msg = ParameterService.add_param(name, identifier)
            if not success:
                logger.warning(f"参数添加失败: {error_msg}")
                messagebox.showerror("错误", error_msg)
                return False
            
            # 创建参数行
            self._create_param_row(name, identifier)
            
            # 通知参数变更
            self._notify_params_change()
            
            # 关闭弹窗
            dialog.destroy()
            logger.debug("参数保存成功")
            return True
            
        except Exception as e:
            error_msg = f"保存参数时出错: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("错误", error_msg)
            return False

    def add_param(self):
        """添加新的自定义参数"""
        logger.info("打开添加参数对话框")
        
        # 创建弹窗
        dialog = tk.Toplevel(self)
        dialog.title("添加自定义参数")
        dialog.transient(self)
        dialog.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(dialog, padding=(20, 20, 20, 10))
        main_frame.pack(fill="both", expand=True)
        
        # 参数名称输入
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill="x", pady=(0, 10))
        ttk.Label(name_frame, text="显示名称:", width=10).pack(side="left")
        name_entry = ttk.Entry(name_frame)
        name_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        # 参数标识输入
        id_frame = ttk.Frame(main_frame)
        id_frame.pack(fill="x", pady=(0, 15))
        ttk.Label(id_frame, text="参数标识:", width=10).pack(side="left")
        identifier_entry = ttk.Entry(id_frame)
        identifier_entry.pack(side="left", padx=5, fill="x", expand=True)
        
        def save():
            """保存参数"""
            name = name_entry.get().strip()
            identifier = identifier_entry.get().strip()
            
            if not name:
                logger.warning("显示名称为空")
                messagebox.showerror("错误", "显示名称不能为空")
                return
                
            self.save_param(name, identifier, dialog)
        
        # 按钮区域
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill="x")
        
        # 创建一个居中的框架来容纳按钮
        center_frame = ttk.Frame(btn_frame)
        center_frame.pack(anchor="center")
        
        ttk.Button(center_frame, text="确定", command=save, width=10).pack(side="left", padx=5)
        ttk.Button(center_frame, text="取消", command=dialog.destroy, width=10).pack(side="left", padx=5)
        
        # 绑定回车键
        dialog.bind('<Return>', lambda e: save())
        
        # 设置焦点
        name_entry.focus()
        
        # 调整窗口大小和位置
        dialog.update_idletasks()
        window_width = 400
        window_height = 150
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        dialog.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        logger.debug("添加参数对话框创建完成")

    def disable_editing(self):
        """禁用参数编辑"""
        logger.info("禁用参数编辑功能")
        # 禁用添加参数按钮
        self.add_param_btn.configure(state="disabled")
        
        # 禁用所有现有参数的删除按钮
        for frame in self.param_frames.values():
            for child in frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.configure(state="disabled")

    def enable_editing(self):
        """启用参数编辑"""
        logger.info("启用参数编辑功能")
        # 启用添加参数按钮
        self.add_param_btn.configure(state="normal")
        
        # 启用所有现有参数的删除按钮
        for frame in self.param_frames.values():
            for child in frame.winfo_children():
                if isinstance(child, ttk.Button):
                    child.configure(state="normal")

    def set_params_change_callback(self, callback: Callable[[List[str], Dict[str, str]], None]):
        """
        设置参数变更回调函数
        
        Args:
            callback: 参数变更时的回调函数
        """
        self.on_params_change = callback

    def _notify_params_change(self):
        """通知参数变化"""
        try:
            if self.on_params_change:
                # 获取参数标识符列表
                params = ParameterService.get_custom_param_identifiers()
                # 获取参数显示名称
                display_names = ParameterService.get_all_param_display_names()
                # 通知变更
                logger.debug(f"通知参数变更 - 参数列表: {params}")
                self.on_params_change(params, display_names)
        except Exception as e:
            error_msg = f"通知参数变化时出错: {str(e)}"
            logger.error(error_msg, exc_info=True)