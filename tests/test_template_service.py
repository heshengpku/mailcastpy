"""
测试模板服务的HTML格式化功能

该测试文件用于验证TemplateService中get_html_content方法，
测试不同格式标签对HTML生成的影响。
"""
import pytest
from src.services.template_service import TemplateService


def create_service(content: str, tags: dict, subject: str = "") -> TemplateService:
    """
    辅助函数，用于创建并初始化TemplateService实例。

    Args:
        content: 文本内容
        tags: 格式标签字典
        subject: 邮件主题

    Returns:
        TemplateService: 初始化后的模板服务实例
    """
    service = TemplateService()
    # 使用默认字体设置Times New Roman, 12pt
    service.update_template(subject=subject, content=content, is_html=True, tags=tags, font_family="Times New Roman", font_size="12")
    return service


def test_get_html_content_basic():
    """测试基本的HTML内容生成"""
    content = "Hello World"
    tags = {}
    service = create_service(content, tags)
    html = service.get_html_content()
    
    assert "Hello&nbsp;World" in html
    assert "<body" in html
    assert "</body>" in html
    assert "<p" in html
    assert "</p>" in html


def test_get_html_content_with_bold():
    """测试带有粗体格式的HTML内容生成

    对于'Hello'，设置索引0-4的字符为bold格式。"""
    content = "Hello World"
    tags = {str(i): ["bold"] for i in range(0, 5)}
    service = create_service(content, tags)
    html = service.get_html_content()
    # 应该存在带有font-weight: bold的span标签包裹'Hello'
    assert '<span style="font-weight: bold' in html
    # 'World'部分应该未被格式化
    assert "World" in html


def test_get_html_content_with_multiple_formats():
    """测试多种格式组合的HTML内容生成

    对于'Hello'，设置索引0-4的字符同时为bold和italic格式。"""
    content = "Hello World"
    tags = {str(i): ["bold", "italic"] for i in range(0, 5)}
    service = create_service(content, tags)
    html = service.get_html_content()
    assert 'font-weight: bold' in html
    assert 'font-style: italic' in html
    assert "Hello" in html
    assert "World" in html


def test_get_html_content_with_font():
    """测试带有字体设置的HTML内容生成

    对于'Hello'，设置索引0-4的字符带有Arial字体和14pt字号。"""
    content = "Hello World"
    tags = {str(i): ["font-family:Arial", "font-size:14"] for i in range(0, 5)}
    service = create_service(content, tags)
    html = service.get_html_content()
    expected = "<span style=\"font-family: 'Arial'; font-size: 14pt\">Hello</span>"
    assert expected in html
    assert "World" in html


def test_get_html_content_with_newlines():
    """测试带有换行符的HTML内容生成

    文本包含换行符，应生成对应的段落标签。"""
    content = "Hello\nWorld"
    tags = {}
    service = create_service(content, tags)
    html = service.get_html_content()
    # 应该有两个段落标签<p>
    assert html.count("<p") == 2
    assert "Hello" in html
    assert "World" in html


def test_get_html_content_with_empty_lines():
    """测试带有空行的HTML内容生成

    文本包含空行，空行中应包含&nbsp;字符，且段落数量应正确。"""
    content = "Hello\n\nWorld"
    tags = {}
    service = create_service(content, tags)
    html = service.get_html_content()
    # 应该有三个<p>标签
    assert html.count("<p") == 3
    assert "&nbsp;" in html 