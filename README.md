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

## 依赖安装

```bash
pip install python-pptx pillow opencv-python playwright requests
playwright install chromium
```

## 注意事项

- 简道云自动化工具中的登录凭证已内置，请根据实际情况修改
- 视频转PPT工具需要安装OpenCV库
- M3U8下载器需要网络连接
- 所有工具都支持自定义参数配置

## 许可证

MIT License
