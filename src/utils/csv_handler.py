"""
CSV文件处理模块

提供CSV文件的读写功能，包括收件人数据的导入导出、
数据验证和格式转换等功能。
"""

import csv
from typing import List, Dict, Set
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class CSVHandler:
    """
    CSV文件处理类
    
    提供CSV文件操作相关功能，包括：
    - 读取收件人数据
    - 验证文件头
    - 写入收件人数据
    """
    
    @staticmethod
    def read_recipients(file_path: str) -> List[Dict[str, str]]:
        """
        读取收件人CSV文件
        
        读取CSV文件并将数据转换为字典列表格式。
        每行数据转换为一个字典，列名作为键。
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            List[Dict[str, str]]: 收件人信息列表
            
        Raises:
            FileNotFoundError: 文件不存在
            UnicodeDecodeError: 文件编码错误
            csv.Error: CSV格式错误
        """
        logger.info(f"开始读取CSV文件: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # 先读取一行获取列名
                reader = csv.reader(file)
                headers = [h.strip() for h in next(reader)]  # 保留原始列名，只去除空格
                logger.debug(f"读取到的列名: {headers}")
                
                # 创建一个字典列表来存储数据
                data = []
                
                # 读取剩余的行
                for row in reader:
                    # 创建一个字典，使用原始列名
                    row_dict = {}
                    for header, value in zip(headers, row):
                        row_dict[header] = value.strip()
                    data.append(row_dict)
                
                logger.info(f"成功读取 {len(data)} 条记录")
                return data
                
        except FileNotFoundError:
            error_msg = f"找不到文件: {file_path}"
            logger.error(error_msg)
            raise
            
        except UnicodeDecodeError:
            error_msg = "文件编码错误，请确保文件使用UTF-8编码"
            logger.error(error_msg)
            raise
            
        except csv.Error as e:
            error_msg = f"CSV文件格式错误: {str(e)}"
            logger.error(error_msg)
            raise

    @staticmethod
    def validate_headers(headers: Set[str], required_params: Set[str]) -> tuple[bool, Set[str]]:
        """
        验证CSV文件头是否包含所需参数（不区分大小写）
        
        检查CSV文件的列名是否包含所有必需的参数。
        
        Args:
            headers: CSV文件头集合
            required_params: 必需参数集合
            
        Returns:
            tuple[bool, Set[str]]: (是否有效, 缺失的参数集合)
        """
        logger.debug("验证CSV文件头")
        
        # 将headers和required_params都转换为小写进行比较
        headers = {h.strip().lower() for h in headers}
        required_params = {p.strip().lower() for p in required_params}
        
        missing_params = required_params - headers
        
        if missing_params:
            logger.warning(f"缺少必需的参数列: {missing_params}")
        else:
            logger.debug("文件头验证通过")
            
        return len(missing_params) == 0, missing_params

    @staticmethod
    def write_recipients(file_path: str, data: List[Dict[str, str]], columns: List[str]) -> None:
        """
        写入收件人数据到CSV文件
        
        将收件人数据保存为CSV文件，只保存指定的列。
        
        Args:
            file_path: CSV文件路径
            data: 收件人数据列表
            columns: 要写入的列名列表
            
        Raises:
            PermissionError: 文件访问权限错误
            OSError: 文件系统错误
        """
        logger.info(f"开始写入CSV文件: {file_path}")
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=columns)
                writer.writeheader()
                
                for recipient in data:
                    # 创建一个新字典，只包含要保存的列
                    row = {k: recipient[k] for k in columns}
                    writer.writerow(row)
                    
            logger.info(f"成功写入 {len(data)} 条记录")
            
        except PermissionError:
            error_msg = f"无法写入文件，请检查文件权限: {file_path}"
            logger.error(error_msg)
            raise
            
        except OSError as e:
            error_msg = f"写入文件时出错: {str(e)}"
            logger.error(error_msg)
            raise 