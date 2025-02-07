"""
收件人列表面板模块

提供收件人数据的显示、编辑、导入导出等功能的图形界面组件。
支持CSV文件的导入导出，双击编辑单个收件人信息，以及实时显示发送状态。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Dict, Set, Optional, Callable, Tuple

from src.utils.csv_handler import CSVHandler
from src.services.parameter_service import ParameterService
from src.services.recipients_service import RecipientsService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RecipientsPanel(ttk.LabelFrame):
    """
    收件人列表面板类
    
    提供收件人数据的管理和显示功能，包括：
    - CSV文件导入导出
    - 收件人信息编辑
    - 发送状态显示
    - 自定义参数同步
    
    Attributes:
        STATUS_COLUMN: 状态列的配置信息
        service: 收件人数据服务
        current_columns: 当前显示的列
        template_params: 模板中使用的参数集合
        on_import: 导入完成的回调函数
    """
    
    # 状态列配置
    STATUS_COLUMN = {
        'id': 'status',
        'display_name': '发送状态',
        'width': 80
    }
    
    def __init__(self, parent):
        """
        初始化收件人列表面板
        
        Args:
            parent: 父级窗口组件
        """
        super().__init__(parent, text="收件人列表")
        logger.info("初始化收件人列表面板")
        
        self.service = RecipientsService()
        # 获取参数列并添加状态列
        param_columns = ParameterService.get_display_columns([])
        self.current_columns = param_columns + [self.STATUS_COLUMN['id']]
        self.template_params: Set[str] = set()  # 存储模板参数
        self.on_import: Optional[Callable[[bool], None]] = None  # 导入回调函数
        self._init_ui()
        logger.debug("收件人列表面板初始化完成")

    def sync_custom_params(self, params: List[str]) -> None:
        """
        同步自定义参数到表格，更新列显示
        
        当参数设置发生变化时，更新表格的列显示，确保与最新的参数配置保持一致。
        
        Args:
            params: 自定义参数列表
        """
        logger.info(f"同步自定义参数: {params}")
        
        # 更新模板参数
        self.template_params = ParameterService.merge_params(params)
        
        # 更新列显示
        param_columns = ParameterService.get_display_columns(params)
        self.current_columns = param_columns + [self.STATUS_COLUMN['id']]
        
        logger.debug(f"更新后的列配置: {self.current_columns}")
        
        # 重新创建表格
        self.create_treeview()
        
        # 刷新数据显示
        if self.service.get_recipients():
            self.refresh_treeview(self.service.get_recipients())

    def _init_ui(self):
        """初始化用户界面
        
        创建工具栏和表格视图，设置基本的界面布局。
        """
        logger.debug("开始初始化用户界面")
        
        # 工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        self.import_btn = ttk.Button(toolbar, text="导入CSV", command=self.import_csv)
        self.import_btn.pack(side="left", padx=2)
        
        self.save_btn = ttk.Button(toolbar, text="保存CSV", command=self.save_csv)
        self.save_btn.pack(side="left", padx=2)

        self.clear_btn = ttk.Button(toolbar, text="清空列表", command=self.clear_recipients)
        self.clear_btn.pack(side="right", padx=2)
        
        # 创建表格
        self.create_treeview()
        logger.debug("用户界面初始化完成")

    def create_treeview(self):
        """创建表格视图
        
        创建或重新创建表格视图，设置列属性和事件绑定。
        包括：
        - 设置列宽和标题
        - 添加滚动条
        - 绑定编辑事件
        """
        logger.debug("开始创建表格视图")
        
        # 如果已存在，先销毁表格和滚动条
        if hasattr(self, 'recipients_tree'):
            self.recipients_tree.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()
        
        # 创建新表格
        columns = self.current_columns
        self.recipients_tree = ttk.Treeview(self, columns=columns, show="headings")
        
        # 获取列宽度
        column_widths = ParameterService.get_column_widths()
        
        # 设置每列的属性
        for col in columns:
            # 设置列宽
            if col == self.STATUS_COLUMN['id']:
                width = self.STATUS_COLUMN['width']
            else:
                width = column_widths.get(col, 150)  # 自定义参数使用更宽的默认宽度
            self.recipients_tree.column(col, width=width)
            
            # 设置列标题
            if col == self.STATUS_COLUMN['id']:
                display_name = self.STATUS_COLUMN['display_name']
            else:
                display_name = ParameterService.get_column_display_name(col)
            self.recipients_tree.heading(col, text=display_name)
        
        # 添加滚动条
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.recipients_tree.yview)
        self.recipients_tree.configure(yscrollcommand=self.scrollbar.set)
        
        self.recipients_tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        self.scrollbar.pack(side="right", fill="y", pady=5)
        
        # 添加编辑功能
        self.recipients_tree.bind('<Double-1>', self.on_double_click)
        self.recipients_tree.bind('<Return>', self.on_double_click)
        
        logger.debug("表格视图创建完成")

    def update_columns(self, custom_params: List[str]) -> None:
        """更新表格列
        
        Args:
            custom_params: 自定义参数列表
        """
        try:
            # 获取参数列并添加状态列
            param_columns = ParameterService.get_display_columns(custom_params)
            self.current_columns = param_columns + [self.STATUS_COLUMN['id']]
            
            print(f"更新列: {custom_params}")
            print(f"当前列: {self.current_columns}")
            
            # 重新创建表格
            self.create_treeview()
            
        except Exception as e:
            print(f"更新列时出错: {str(e)}")
            messagebox.showerror("错误", f"更新列失败: {str(e)}")

    def refresh_treeview(self, data: List[Dict[str, str]]):
        """
        刷新表格数据显示
        
        清空当前表格内容，并使用新的数据重新填充表格。
        
        Args:
            data: 收件人数据列表，每个字典包含一个收件人的所有字段
        """
        logger.debug(f"开始刷新表格数据，共 {len(data)} 条记录")
        
        # 清空现有数据
        for item in self.recipients_tree.get_children():
            self.recipients_tree.delete(item)
        
        # 添加新数据
        for recipient in data:
            values = []
            for col in self.current_columns:
                values.append(recipient.get(col, ""))
            self.recipients_tree.insert("", "end", values=values)
        
        logger.debug("表格数据刷新完成")

    def on_double_click(self, event):
        """
        处理双击编辑事件
        
        创建一个弹窗来编辑选中的收件人信息，包括：
        - 显示所有可编辑字段
        - 验证输入数据
        - 保存修改结果
        
        Args:
            event: 鼠标双击事件对象
        """
        try:
            # 确保有选中的项
            selection = self.recipients_tree.selection()
            if not selection:
                logger.debug("未选中任何项，忽略双击事件")
                return
                
            item = selection[0]
            row_index = self.recipients_tree.index(item)
            recipient = self.service.get_recipient(row_index)
            
            logger.info(f"开始编辑收件人信息: {recipient.get('email', 'N/A')}")
            
            # 创建编辑窗口
            edit_window = self._create_edit_window(recipient, item, row_index)
            
        except Exception as e:
            error_msg = f"编辑收件人信息时出错: {str(e)}"
            logger.error(error_msg, exc_info=True)
            messagebox.showerror("错误", error_msg)

    def _create_edit_window(self, recipient: Dict[str, str], item: str, row_index: int) -> tk.Toplevel:
        """
        创建编辑窗口
        
        Args:
            recipient: 收件人数据
            item: 树形视图中的项ID
            row_index: 行索引
            
        Returns:
            tk.Toplevel: 编辑窗口对象
        """
        logger.debug("创建编辑窗口")
        
        edit_window = tk.Toplevel(self)
        edit_window.title("编辑收件人信息")
        edit_window.transient(self)
        edit_window.grab_set()
        
        # 创建主框架
        main_frame = ttk.Frame(edit_window, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # 创建滚动框架
        scroll_container = ttk.Frame(main_frame)
        scroll_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # 配置滚动区域
        canvas, scrollbar, scrollable_frame = self._setup_scrollable_frame(scroll_container)
        
        # 创建输入字段
        entries = self._create_input_fields(scrollable_frame, recipient)
        
        # 创建按钮
        self._create_edit_buttons(main_frame, edit_window, entries, recipient, item, row_index)
        
        # 设置窗口大小和位置
        self._setup_window_geometry(edit_window, main_frame)
        
        logger.debug("编辑窗口创建完成")
        return edit_window

    def set_import_callback(self, callback: Callable[[bool], None]):
        """设置导入回调函数
        
        Args:
            callback: 导入完成的回调函数，参数为是否导入成功
        """
        self.on_import = callback

    def import_csv(self):
        """
        导入CSV文件
        
        打开文件选择对话框，导入并验证CSV文件数据，然后更新显示。
        包括：
        - 验证必需字段
        - 检查模板参数
        - 更新表格显示
        """
        logger.info("开始导入CSV文件")
        
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            logger.debug("用户取消了文件选择")
            return
            
        # 使用服务导入CSV
        success, error_msg, data = self.service.import_csv(file_path)
        
        if not success:
            logger.error(f"CSV导入失败: {error_msg}")
            messagebox.showerror("错误", error_msg)
            if self.on_import:
                self.on_import(False)
            return
        
        # 验证自定义参数
        if self.template_params:
            is_valid, undefined_params = self.service.validate_template_params(self.template_params)
            if not is_valid:
                error_msg = f"CSV文件缺少必需的参数列：{', '.join(undefined_params)}"
                logger.error(error_msg)
                messagebox.showerror("错误", 
                    f"{error_msg}\n请确保CSV文件包含所有模板中使用的参数。")
                if self.on_import:
                    self.on_import(False)
                return
        
        # 更新显示
        custom_params = ParameterService.get_custom_param_identifiers()
        param_columns = ParameterService.get_display_columns(custom_params)
        self.current_columns = param_columns + [self.STATUS_COLUMN['id']]
        self.refresh_treeview(data)
        
        logger.info(f"成功导入 {len(data)} 条收件人信息")
        messagebox.showinfo("成功", f"已导入 {len(data)} 条收件人信息")
        
        # 调用导入成功回调
        if self.on_import:
            self.on_import(True)

    def save_csv(self):
        """
        保存CSV文件
        
        打开文件保存对话框，将当前收件人数据保存为CSV文件。
        """
        logger.info("开始保存CSV文件")
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        if not file_path:
            logger.debug("用户取消了文件保存")
            return
        
        # 获取所有列（除了状态列）
        columns = [col for col in self.current_columns 
                  if col != self.STATUS_COLUMN['id']]
        
        # 使用服务保存CSV
        success, error_msg = self.service.save_csv(file_path, columns)
        
        if success:
            logger.info("CSV文件保存成功")
            messagebox.showinfo("成功", "数据已保存")
        else:
            logger.error(f"CSV保存失败: {error_msg}")
            messagebox.showerror("错误", error_msg)

    def update_status(self, email: str, status: str):
        """
        更新指定收件人的发送状态
        
        Args:
            email: 收件人邮箱
            status: 新的发送状态
        """
        logger.debug(f"更新发送状态 - 邮箱: {email}, 状态: {status}")
        
        if self.service.update_status(email, status):
            # 更新显示
            for item in self.recipients_tree.get_children():
                if self.recipients_tree.item(item)['values'][0] == email:
                    values = list(self.recipients_tree.item(item)['values'])
                    status_index = self.current_columns.index('status')
                    values[status_index] = status
                    self.recipients_tree.item(item, values=values)
                    logger.debug("状态更新成功")
                    break

    def get_recipients(self) -> List[Dict[str, str]]:
        """
        获取收件人列表
        
        Returns:
            List[Dict[str, str]]: 收件人数据列表
        """
        return self.service.get_recipients()

    def clear_recipients(self):
        """
        清空收件人列表
        
        清空当前所有收件人数据，并更新显示。
        """
        if not self.service.get_recipients():
            logger.debug("收件人列表已经为空")
            messagebox.showinfo("提示", "收件人列表已经是空的")
            return
            
        if messagebox.askyesno("确认", "确定要清空收件人列表吗？\n此操作不可撤销。"):
            logger.info("清空收件人列表")
            self.service.clear_data()
            # 调用导入回调（参数为False表示清空）
            if self.on_import:
                self.on_import(False)
            # 刷新显示
            self.refresh_treeview([])
            messagebox.showinfo("成功", "收件人列表已清空")
            logger.info("收件人列表已清空")

    def _setup_scrollable_frame(self, container: ttk.Frame) -> Tuple[tk.Canvas, ttk.Scrollbar, ttk.Frame]:
        """
        创建可滚动的框架
        
        Args:
            container: 容器框架
            
        Returns:
            Tuple[tk.Canvas, ttk.Scrollbar, ttk.Frame]: 画布、滚动条和可滚动框架
        """
        logger.debug("创建可滚动框架")
        
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        def configure_scroll_region(event):
            """配置滚动区域并控制滚动条显示"""
            canvas.configure(scrollregion=canvas.bbox("all"))
            # 判断是否需要显示滚动条
            if scrollable_frame.winfo_reqheight() <= canvas.winfo_height():
                scrollbar.pack_forget()
                canvas.pack(side="left", fill="both", expand=True)
            else:
                canvas.pack(side="left", fill="both", expand=True, padx=(0, 5))
                scrollbar.pack(side="right", fill="y")
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        
        logger.debug("可滚动框架创建完成")
        return canvas, scrollbar, scrollable_frame

    def _create_input_fields(self, parent: ttk.Frame, recipient: Dict[str, str]) -> Dict[str, ttk.Entry]:
        """
        创建输入字段
        
        Args:
            parent: 父级框架
            recipient: 收件人数据
            
        Returns:
            Dict[str, ttk.Entry]: 字段名到输入框的映射
        """
        logger.debug("创建输入字段")
        
        entries = {}
        
        # 计算标签最大宽度
        max_label_width = 0
        display_names = []
        for col in self.current_columns:
            if col != self.STATUS_COLUMN['id']:
                display_name = ParameterService.get_column_display_name(col)
                display_names.append((col, display_name))
                width = len(display_name) * 2  # 估算中文字符宽度
                max_label_width = max(max_label_width, width)
        
        # 添加参数输入框
        for col, display_name in display_names:
            frame = ttk.Frame(parent)
            frame.pack(fill="x", pady=2)  # 将 pady 从5修改为2
            
            label = ttk.Label(frame, text=f"{display_name}:", width=max_label_width)
            label.pack(side="left", padx=(5, 10))
            
            entry = ttk.Entry(frame)
            entry.insert(0, recipient.get(col, ""))
            entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
            entry.configure(width=40)
            
            entries[col] = entry
        
        logger.debug(f"创建了 {len(entries)} 个输入字段")
        return entries

    def _create_edit_buttons(self, parent: ttk.Frame, window: tk.Toplevel, 
                           entries: Dict[str, ttk.Entry], recipient: Dict[str, str],
                           item: str, row_index: int):
        """
        创建编辑窗口的按钮

        Args:
            parent: 父级框架
            window: 编辑窗口
            entries: 输入框字典
            recipient: 收件人数据
            item: 树形视图项ID
            row_index: 行索引
        """
        logger.debug("创建编辑窗口按钮")

        def validate_input() -> bool:
            """验证输入数据"""
            for col, entry in entries.items():
                value = entry.get().strip()
                display_name = ParameterService.get_column_display_name(col)
                
                # 检查必填字段
                if col in ['email', 'name'] and not value:
                    error_msg = f"{display_name}不能为空"
                    logger.warning(f"输入验证失败: {error_msg}")
                    messagebox.showerror("错误", error_msg)
                    entry.focus()
                    return False

                # 验证邮箱格式
                if col == 'email' and '@' not in value:
                    error_msg = "请输入有效的邮箱地址"
                    logger.warning(f"输入验证失败: {error_msg}")
                    messagebox.showerror("错误", error_msg)
                    entry.focus()
                    return False

            return True

        def save_edit():
            """保存编辑内容"""
            if not validate_input():
                return

            try:
                logger.info("开始保存编辑内容")
                # 更新数据
                new_values = []
                new_data = recipient.copy()
                for col in self.current_columns:
                    if col == self.STATUS_COLUMN['id']:
                        new_values.append(recipient[col])
                    else:
                        value = entries[col].get().strip()
                        new_data[col] = value
                        new_values.append(value)

                # 使用服务更新数据
                self.service.update_recipient(row_index, new_data)

                # 更新treeview
                self.recipients_tree.item(item, values=new_values)
                logger.info("编辑内容保存成功")
                window.destroy()

            except Exception as e:
                error_msg = f"保存失败: {str(e)}"
                logger.error(error_msg, exc_info=True)
                messagebox.showerror("错误", error_msg)

        def cancel_edit():
            """取消编辑"""
            logger.debug("取消编辑")
            window.destroy()
        
        # 按钮区域
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill="x", pady=(0, 5))
        
        # 创建一个居中的框架来容纳按钮
        center_frame = ttk.Frame(btn_frame)
        center_frame.pack(anchor="center")
        
        ttk.Button(center_frame, text="保存", command=save_edit, width=10).pack(side="left", padx=5)
        ttk.Button(center_frame, text="取消", command=cancel_edit, width=10).pack(side="left", padx=5)
        
        logger.debug("编辑窗口按钮创建完成")

    def _setup_window_geometry(self, window: tk.Toplevel, content_frame: ttk.Frame):
        """
        设置窗口大小和位置
        
        Args:
            window: 目标窗口
            content_frame: 内容框架
        """
        logger.debug("设置窗口大小和位置")
        
        window.update_idletasks()
        
        # 计算合适的窗口大小
        frame_width = max(500, content_frame.winfo_reqwidth() + 40)  # 设置最小宽度为500
        frame_height = min(content_frame.winfo_reqheight() + 60,
                         window.winfo_screenheight() * 0.8)
        
        # 设置窗口大小和位置
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - frame_width) // 2
        y = (screen_height - frame_height) // 2
        window.geometry(f"{frame_width}x{frame_height}+{x}+{y}")
        
        logger.debug(f"窗口大小设置为: {frame_width}x{frame_height}") 