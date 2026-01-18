# Common Tools Python

这是一个Python工具集，包含多个实用的自动化和转换工具。

## 工具列表

### 1. image_2_ppt.py - 图片转PPT工具

将文件夹下的所有图片转换为PPT文件。

**主要功能：**
- 支持多种图片格式（JPG、JPEG、PNG、GIF、BMP、TIFF、WEBP）
- 自动按文件名排序
- 保持图片宽高比，自动调整大小以适应幻灯片
- 可选添加页码
- 自定义幻灯片尺寸

**使用示例：**
```python
from image_2_ppt import ImageToPPT

converter = ImageToPPT(
    image_folder="images",
    output_path="output.pptx",
    slide_width=10,
    slide_height=5.625
)
converter.convert()
```

### 2. jdy_auto_form_tool.py - 简道云自动化工具

使用Playwright实现简道云平台的自动化操作。

**主要功能：**
- 自动登录简道云平台
- 支持无头模式和有头模式
- 自动处理表单填写
- 支持手动验证码处理
- 完整的日志记录

**使用示例：**
```python
from jdy_auto_form_tool import JDYAutomationPlaywright

automation = JDYAutomationPlaywright(headless=False)
automation.setup_browser()
automation.login()
# 执行其他自动化操作...
automation.close()
```

### 3. jdy_automation_playwright.py - 简道云自动化工具（Playwright版本）

使用Playwright实现更快速、更可靠的简道云自动化操作。

**主要功能：**
- 内置登录凭证
- 自动登录简道云平台
- 支持多种选择器策略
- 自动处理验证码
- 完整的错误处理和日志记录

**使用示例：**
```python
from jdy_automation_playwright import JDYAutomationPlaywright

automation = JDYAutomationPlaywright(headless=False)
automation.setup_browser()
automation.login(manual_verify=True)
# 执行其他自动化操作...
automation.close()
```

### 4. m3u8_download.py - M3U8视频下载器

支持下载和合并m3u8视频流。

**主要功能：**
- 解析m3u8文件，获取所有视频片段
- 多线程并发下载，提高下载速度
- 自动合并视频片段
- 支持断点续传
- 自定义并发下载数

**使用示例：**
```python
from m3u8_download import M3U8Downloader

downloader = M3U8Downloader(
    m3u8_url="https://example.com/video.m3u8",
    output_dir="downloads",
    max_workers=10
)
downloader.download()
```

### 5. video_2_ppt.py - 视频转PPT工具

从视频中提取PPT幻灯片并生成PPT文件。

**主要功能：**
- 从视频中提取关键帧
- 基于相似度检测幻灯片变化
- 自动过滤重复幻灯片
- 可设置最小时间间隔
- 支持自定义相似度阈值

**使用示例：**
```python
from video_2_ppt import VideoToPPT

converter = VideoToPPT(
    video_path="presentation.mp4",
    output_path="output.pptx",
    similarity_threshold=0.95,
    min_interval=2.0
)
converter.convert()
```

## PDF 工具集

### 6. pdf/merge_pdfs.py - PDF 合并工具

将多个 PDF 文件合并为一个文件，可选添加连续页码。

**主要功能：**
- 合并多个 PDF 文件
- 可选添加连续页码（页码位于页面底部中央）
- 自动处理页面尺寸
- 支持任意数量的 PDF 文件

**使用示例：**
```python
from pdf.merge_pdfs import merge_pdfs

pdf_files = ["file1.pdf", "file2.pdf", "file3.pdf"]
output_path = "merged.pdf"
merge_pdfs(pdf_files, output_path, add_numbers=True)
```

### 7. pdf/pdf_edit_gui.py - PDF 编辑器 GUI

图形化界面的 PDF 编辑工具，提供直观的 PDF 操作界面。

**主要功能：**
- 打开和预览 PDF 文件
- 页面导航（上一页/下一页）
- 删除指定页面
- 旋转页面（90度）
- 文本查找和替换
- 拆分 PDF（按页码范围、提取指定页面、每隔 N 页）
- 保存编辑后的 PDF
- 显示 PDF 元数据和属性

**使用示例：**
```bash
python pdf/pdf_edit_gui.py
```

### 8. pdf/pdf_split.py - PDF 拆分工具

将 PDF 文件按不同方式拆分为多个文件。

**主要功能：**
- 按页码范围拆分（如：1-10, 11-20）
- 提取指定页码到单独文件
- 每隔 N 页拆分一个文件
- 自动创建输出目录
- 详细的处理日志

**使用示例：**
```python
from pdf.pdf_split import split_pdf_by_page_range, split_pdf_by_page_numbers, split_pdf_every_n_pages

# 按页码范围拆分
split_pdf_by_page_range("input.pdf", "output_dir", [(1, 10), (11, 20)])

# 提取指定页码
split_pdf_by_page_numbers("input.pdf", "output_dir", [1, 3, 5, 7])

# 每隔 N 页拆分
split_pdf_every_n_pages("input.pdf", "output_dir", pages_per_file=5)
```

### 9. pdf/pdf_table_extractor.py - PDF 表格提取工具

从 PDF 文件中提取表格数据并导出到 Excel。

**主要功能：**
- 提取 PDF 中的所有表格
- 将表格合并到单个 Excel 文件
- 支持固定表头（17列银行流水格式）
- 自动处理表格列数不一致的情况
- 支持批量处理多个 PDF 文件
- 提取所有文本内容到文本文件

**使用示例：**
```python
from pdf.pdf_table_extractor import extract_tables_from_pdf, batch_extract_tables

# 提取单个 PDF 的表格
extract_tables_from_pdf("input.pdf", "output_dir")

# 批量提取目录下所有 PDF 的表格
batch_extract_tables("pdf_directory", "output_dir")
```

## 依赖安装

```bash
pip install python-pptx pillow opencv-python playwright requests pypdf reportlab pdfplumber pandas openpyxl PyMuPDF
playwright install chromium
```

## 注意事项

- 简道云自动化工具中的登录凭证已内置，请根据实际情况修改
- 视频转PPT工具需要安装OpenCV库
- M3U8下载器需要网络连接
- 所有工具都支持自定义参数配置

## 许可证

MIT License
