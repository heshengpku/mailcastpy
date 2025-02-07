"""
参数管理服务模块

提供参数的管理、验证和同步功能，包括默认参数和自定义参数的处理。
支持参数的添加、删除、验证和显示名称管理。
"""

from typing import List, Dict, Set, Tuple
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class ParameterService:
    """
    参数管理服务类
    
    提供参数管理相关功能，包括：
    - 默认参数管理
    - 自定义参数管理
    - 参数验证
    - 显示名称管理
    
    Attributes:
        _custom_params: 自定义参数列表，每项为 (显示名称, 标识符) 元组
        _SYSTEM_PARAMS: 系统默认参数字典
    """
    
    _custom_params: List[Tuple[str, str]] = []  # [(显示名称, 标识符)]
    _SYSTEM_PARAMS = {
        'email': '邮箱地址',
        'name': '收件人姓名'
    }
    
    @classmethod
    def add_param(cls, display_name: str, identifier: str) -> Tuple[bool, str]:
        """
        添加自定义参数
        
        Args:
            display_name: 显示名称
            identifier: 参数标识符
            
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        logger.info(f"添加自定义参数 - 显示名称: {display_name}, 标识符: {identifier}")
        
        # 验证参数标识符
        existing_ids = {id for _, id in cls._custom_params}
        is_valid, error_msg = cls.validate_param_identifier(identifier, existing_ids)
        if not is_valid:
            logger.warning(f"参数标识符验证失败: {error_msg}")
            return False, error_msg
            
        # 添加参数
        cls._custom_params.append((display_name, identifier))
        logger.debug("参数添加成功")
        return True, ""
    
    @classmethod
    def remove_param(cls, identifier: str) -> bool:
        """
        移除自定义参数
        
        Args:
            identifier: 参数标识符
            
        Returns:
            bool: 是否成功移除
        """
        logger.info(f"移除自定义参数 - 标识符: {identifier}")
        for i, (_, param_id) in enumerate(cls._custom_params):
            if param_id.lower() == identifier.lower():
                cls._custom_params.pop(i)
                logger.debug("参数移除成功")
                return True
        logger.warning("未找到要移除的参数")
        return False
    
    @classmethod
    def get_custom_params(cls) -> List[Tuple[str, str]]:
        """
        获取所有自定义参数
        
        Returns:
            List[Tuple[str, str]]: 自定义参数列表，每个元素为 (显示名称, 标识符)
        """
        return cls._custom_params.copy()
    
    @classmethod
    def get_custom_param_identifiers(cls) -> List[str]:
        """
        获取自定义参数标识符列表
        
        Returns:
            List[str]: 参数标识符列表
        """
        return [identifier for _, identifier in cls._custom_params]
    
    @classmethod
    def get_all_param_display_names(cls) -> Dict[str, str]:
        """
        获取所有参数的显示名称（包括默认参数和自定义参数）
        
        Returns:
            Dict[str, str]: 参数标识符到显示名称的映射
        """
        names = dict(cls.get_default_params())  # 获取默认参数
        # 添加自定义参数
        for display_name, identifier in cls._custom_params:
            names[identifier.lower()] = display_name
        return names
    
    @classmethod
    def clear_custom_params(cls):
        """清空所有自定义参数"""
        logger.info("清空所有自定义参数")
        cls._custom_params.clear()

    @staticmethod
    def validate_param_identifier(identifier: str, existing_ids: Set[str]) -> Tuple[bool, str]:
        """
        验证参数标识符
        
        检查标识符是否合法且不重复。
        
        Args:
            identifier: 参数标识符
            existing_ids: 现有的参数标识符集合
            
        Returns:
            Tuple[bool, str]: (是否有效, 错误信息)
        """
        logger.debug(f"验证参数标识符: {identifier}")
        
        # 检查是否为空
        if not identifier:
            logger.warning("参数标识符为空")
            return False, "参数标识符不能为空"
            
        # 检查是否重复（不区分大小写）
        if identifier.lower() in {id.lower() for id in existing_ids}:
            logger.warning("参数标识符重复")
            return False, "参数标识符已存在"
            
        # 检查格式（只允许字母、数字和下划线）
        if not identifier.replace('_', '').isalnum():
            logger.warning("参数标识符格式不正确")
            return False, "参数标识符只能包含字母、数字和下划线"
            
        logger.debug("参数标识符验证通过")
        return True, ""

    @classmethod
    def get_system_params(cls) -> Dict[str, str]:
        """
        获取系统参数
        
        Returns:
            Dict[str, str]: 系统参数的显示名称映射
        """
        return cls._SYSTEM_PARAMS.copy()
    
    @classmethod
    def get_display_columns(cls, custom_params: List[str]) -> List[str]:
        """
        获取显示列的顺序（包括系统参数和自定义参数）
        
        Args:
            custom_params: 自定义参数列表
            
        Returns:
            List[str]: 显示列的顺序
        """
        # 固定顺序：email, name, 自定义参数
        return ["email", "name"] + custom_params
    
    @classmethod
    def get_column_display_name(cls, column: str) -> str:
        """
        获取列的显示名称
        
        Args:
            column: 列标识符
            
        Returns:
            str: 显示名称
        """
        # 先检查是否是系统参数
        if column.lower() in cls._SYSTEM_PARAMS:
            return cls._SYSTEM_PARAMS[column.lower()]
        
        # 再检查是否是自定义参数
        for display_name, identifier in cls._custom_params:
            if identifier.lower() == column.lower():
                return display_name
                
        # 如果都不是，返回原始标识符
        return column
    
    @classmethod
    def get_column_widths(cls) -> Dict[str, int]:
        """
        获取列的默认宽度
        
        Returns:
            Dict[str, int]: 列标识符到宽度的映射
        """
        return {
            "email": 200,
            "name": 100
        }
    
    @classmethod
    def sync_params_with_data(cls, params: List[str], data: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        同步参数到数据中
        
        Args:
            params: 参数列表
            data: 原始数据
            
        Returns:
            List[Dict[str, str]]: 更新后的数据
        """
        logger.info("同步参数到数据")
        # 系统参数和自定义参数列
        valid_columns = set(cls._SYSTEM_PARAMS.keys()) | set(params)
        updated_data = []
        
        for row in data:
            new_row = {}
            # 保留有效的列和状态列
            for col in valid_columns:
                new_row[col] = row.get(col, "")
            # 保留状态列
            if 'status' in row:
                new_row['status'] = row['status']
            updated_data.append(new_row)
            
        logger.debug(f"数据同步完成，共 {len(updated_data)} 条记录")
        return updated_data

    @staticmethod
    def get_default_params() -> Dict[str, str]:
        """
        获取默认参数
        
        Returns:
            Dict[str, str]: 默认参数的显示名称和标识符映射
        """
        return {
            "name": "收件人姓名",
            "email": "邮箱地址"
        }

    @staticmethod
    def validate_required_params(headers: Set[str]) -> Tuple[bool, Set[str]]:
        """
        验证必需参数是否存在
        
        Args:
            headers: 当前的参数集合
            
        Returns:
            Tuple[bool, Set[str]]: (是否有效, 缺失的参数集合)
        """
        logger.debug("验证必需参数")
        required = {'name', 'email'}
        headers_lower = {h.lower() for h in headers}
        missing = required - headers_lower
        
        if missing:
            logger.warning(f"缺少必需参数: {missing}")
        else:
            logger.debug("必需参数验证通过")
            
        return len(missing) == 0, missing

    @staticmethod
    def merge_params(custom_params: List[str]) -> Set[str]:
        """
        合并默认参数和自定义参数
        
        Args:
            custom_params: 自定义参数列表
            
        Returns:
            Set[str]: 所有可用参数的集合
        """
        default_params = {'name', 'email'}
        return default_params | set(custom_params)

    @staticmethod
    def validate_template_params(template_params: Set[str], available_params: Set[str]) -> Tuple[bool, Set[str]]:
        """
        验证模板参数是否都已定义
        
        Args:
            template_params: 模板中使用的参数集合
            available_params: 可用参数集合
            
        Returns:
            Tuple[bool, Set[str]]: (是否验证通过, 未定义的参数集合)
        """
        logger.debug("验证模板参数")
        # 将参数转换为小写进行比较
        template_params_lower = {p.lower() for p in template_params}
        available_params_lower = {p.lower() for p in available_params}
        undefined_params = template_params_lower - available_params_lower
        
        if undefined_params:
            logger.warning(f"发现未定义的模板参数: {undefined_params}")
        else:
            logger.debug("模板参数验证通过")
            
        return len(undefined_params) == 0, undefined_params 