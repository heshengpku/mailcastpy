"""
收件人数据管理服务模块

提供收件人数据的管理功能，包括CSV文件的导入导出、
状态更新、数据验证等功能。支持模板参数验证和数据同步。
"""

from typing import List, Dict, Set, Tuple
from src.utils.csv_handler import CSVHandler
from src.services.parameter_service import ParameterService
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RecipientsService:
    """
    收件人数据管理服务类
    
    提供收件人数据管理相关功能，包括：
    - CSV文件导入导出
    - 收件人状态管理
    - 数据验证
    - 模板参数验证
    
    Attributes:
        recipients_data: 收件人数据列表，每项为一个字典
    """
    
    def __init__(self):
        """初始化收件人服务"""
        logger.info("初始化收件人数据管理服务")
        self.recipients_data: List[Dict[str, str]] = []
    
    def import_csv(self, file_path: str) -> Tuple[bool, str, List[Dict[str, str]]]:
        """
        导入CSV文件
        
        读取并验证CSV文件内容，确保包含必需的字段。
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            Tuple[bool, str, List[Dict[str, str]]]: (是否成功, 错误信息, 导入的数据)
        """
        try:
            logger.info(f"开始导入CSV文件: {file_path}")
            
            # 读取CSV文件
            data = CSVHandler.read_recipients(file_path)
            
            if not data:
                logger.warning("CSV文件为空")
                return False, "CSV文件为空", []
            
            # 验证必需字段
            headers = set(data[0].keys())
            is_valid, missing_params = ParameterService.validate_required_params(headers)
            if not is_valid:
                error_msg = (
                    f"CSV文件缺少必需的参数列：{', '.join(missing_params)}\n"
                    "请确保CSV文件包含以下列：\n"
                    "- email 或 Email（邮箱地址）\n"
                    "- name 或 Name（收件人姓名）"
                )
                logger.warning(f"CSV文件验证失败: {error_msg}")
                return False, error_msg, []
            
            # 添加状态列
            for recipient in data:
                recipient['status'] = "待发送"
            
            self.recipients_data = data
            logger.info(f"成功导入 {len(data)} 条收件人数据")
            return True, "", data
            
        except Exception as e:
            error_msg = f"导入失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg, []
    
    def save_csv(self, file_path: str, columns: List[str]) -> Tuple[bool, str]:
        """
        保存CSV文件
        
        将当前收件人数据保存到CSV文件。
        
        Args:
            file_path: 保存路径
            columns: 要保存的列（不包括状态列）
            
        Returns:
            Tuple[bool, str]: (是否成功, 错误信息)
        """
        try:
            logger.info(f"开始保存CSV文件: {file_path}")
            
            if not self.recipients_data:
                logger.warning("没有数据可保存")
                return False, "没有数据可保存"
                
            CSVHandler.write_recipients(file_path, self.recipients_data, columns)
            logger.info(f"成功保存 {len(self.recipients_data)} 条收件人数据")
            return True, ""
            
        except Exception as e:
            error_msg = f"保存失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    def clear_data(self) -> None:
        """清空收件人数据"""
        logger.info("清空收件人数据")
        self.recipients_data = []
    
    def update_status(self, email: str, status: str) -> bool:
        """
        更新收件人状态
        
        Args:
            email: 收件人邮箱
            status: 新状态
            
        Returns:
            bool: 是否找到并更新了状态
        """
        logger.debug(f"更新收件人状态 - 邮箱: {email}, 状态: {status}")
        for recipient in self.recipients_data:
            if recipient['email'] == email:
                recipient['status'] = status
                logger.debug("状态更新成功")
                return True
        logger.warning(f"未找到收件人: {email}")
        return False
    
    def validate_template_params(self, template_params: Set[str]) -> Tuple[bool, Set[str]]:
        """
        验证模板参数是否都存在
        
        检查模板中使用的参数是否都在收件人数据中定义。
        
        Args:
            template_params: 模板中使用的参数集合
            
        Returns:
            Tuple[bool, Set[str]]: (是否验证通过, 未定义的参数集合)
        """
        logger.debug("验证模板参数")
        if not self.recipients_data:
            logger.debug("收件人数据为空，跳过验证")
            return True, set()
            
        headers = set(self.recipients_data[0].keys())
        is_valid, undefined_params = ParameterService.validate_template_params(template_params, headers)
        
        if not is_valid:
            logger.warning(f"发现未定义的模板参数: {undefined_params}")
        else:
            logger.debug("模板参数验证通过")
            
        return is_valid, undefined_params
    
    def get_recipients(self) -> List[Dict[str, str]]:
        """
        获取收件人列表
        
        Returns:
            List[Dict[str, str]]: 收件人数据列表
        """
        return self.recipients_data
    
    def get_recipient(self, index: int) -> Dict[str, str]:
        """
        获取指定索引的收件人
        
        Args:
            index: 收件人索引
            
        Returns:
            Dict[str, str]: 收件人数据
        """
        logger.debug(f"获取收件人数据 - 索引: {index}")
        return self.recipients_data[index]
    
    def update_recipient(self, index: int, data: Dict[str, str]) -> None:
        """
        更新指定索引的收件人数据
        
        Args:
            index: 收件人索引
            data: 新的收件人数据
        """
        logger.debug(f"更新收件人数据 - 索引: {index}")
        if 0 <= index < len(self.recipients_data):
            self.recipients_data[index] = data
            logger.debug("收件人数据更新成功")
        else:
            logger.warning(f"无效的索引: {index}") 