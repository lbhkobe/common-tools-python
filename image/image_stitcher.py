"""
图片拼接工具
支持横向和垂直拼接多张图片
"""

from PIL import Image
import os
from pathlib import Path
import argparse


class ImageStitcher:
    """图片拼接器"""
    
    def __init__(self, images, output_path="stitched_image.jpg", 
                 direction="horizontal", spacing=0, background_color=(255, 255, 255)):
        """
        初始化拼接器
        
        Args:
            images: 图片路径列表
            output_path: 输出图片路径
            direction: 拼接方向，"horizontal" 或 "vertical"
            spacing: 图片之间的间距（像素）
            background_color: 背景颜色 (R, G, B)
        """
        self.images = [Path(img) for img in images]
        self.output_path = Path(output_path)
        self.direction = direction.lower()
        self.spacing = spacing
        self.background_color = background_color
        
        # 验证图片文件
        self._validate_images()
    
    def _validate_images(self):
        """验证所有图片文件是否存在"""
        valid_images = []
        for img_path in self.images:
            if not img_path.exists():
                print(f"警告: 图片文件不存在: {img_path}")
                continue
            
            try:
                # 尝试打开图片验证格式
                with Image.open(img_path) as img:
                    img.verify()
                valid_images.append(img_path)
            except Exception as e:
                print(f"警告: 图片文件格式错误 {img_path}: {e}")
        
        if not valid_images:
            raise ValueError("没有有效的图片文件")
        
        self.images = valid_images
    
    def _load_images(self):
        """加载所有图片并调整大小"""
        loaded_images = []
        
        for img_path in self.images:
            img = Image.open(img_path)
            # 转换为RGB模式（如果图片是RGBA或其他模式）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # 将图片数据加载到内存中，避免文件被关闭后无法访问
            img.load()
            loaded_images.append(img)
        
        return loaded_images
    
    def _calculate_size(self, images):
        """计算拼接后图片的尺寸"""
        if self.direction == "horizontal":
            # 横向拼接：宽度相加，高度取最大值
            total_width = sum(img.width for img in images) + (len(images) - 1) * self.spacing
            max_height = max(img.height for img in images)
            return total_width, max_height
        else:
            # 垂直拼接：高度相加，宽度取最大值
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images) + (len(images) - 1) * self.spacing
            return max_width, total_height
    
    def _create_background(self, width, height):
        """创建背景图片"""
        return Image.new('RGB', (width, height), self.background_color)
    
    def _paste_images(self, background, images):
        """将图片粘贴到背景上"""
        if self.direction == "horizontal":
            # 横向拼接
            x_offset = 0
            for img in images:
                background.paste(img, (x_offset, 0))
                x_offset += img.width + self.spacing
        else:
            # 垂直拼接
            y_offset = 0
            for img in images:
                background.paste(img, (0, y_offset))
                y_offset += img.height + self.spacing
        
        return background
    
    def stitch(self):
        """执行图片拼接"""
        try:
            print("正在加载图片...")
            images = self._load_images()
            
            print(f"成功加载 {len(images)} 张图片")
            for i, img in enumerate(images):
                print(f"  {i+1}. {img.width}x{img.height}")
            
            print(f"\n拼接方向: {self.direction}")
            print(f"图片间距: {self.spacing} 像素")
            print(f"背景颜色: RGB{self.background_color}")
            
            # 计算输出尺寸
            output_width, output_height = self._calculate_size(images)
            print(f"\n输出尺寸: {output_width}x{output_height}")
            
            # 创建背景
            print("正在创建背景...")
            background = self._create_background(output_width, output_height)
            
            # 粘贴图片
            print("正在拼接图片...")
            result = self._paste_images(background, images)
            
            # 保存结果
            print(f"正在保存结果到: {self.output_path}")
            result.save(self.output_path, quality=95, optimize=True)
            
            print(f"\n拼接完成！")
            print(f"输出文件: {self.output_path.absolute()}")
            print(f"文件大小: {self.output_path.stat().st_size / 1024:.2f} KB")
            
            return True
            
        except Exception as e:
            print(f"\n拼接过程出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


# 图片地址数组 - 维护要拼接的图片路径
IMAGE_FILES = [
    "D:\\ChromeDownload\\lbh1.jpg",
    "D:\\ChromeDownload\\lbh2.jpg"
    # 可以在这里添加更多图片路径
]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='图片拼接工具')
    parser.add_argument('images', nargs='*', help='图片文件路径（可选，如果不提供则使用内置数组）')
    parser.add_argument('-o', '--output', default='stitched_image.jpg', 
                       help='输出文件路径 (默认: stitched_image.jpg)')
    parser.add_argument('-d', '--direction', choices=['horizontal', 'vertical'], 
                       default='horizontal', help='拼接方向 (默认: horizontal)')
    parser.add_argument('-s', '--spacing', type=int, default=0, 
                       help='图片间距（像素） (默认: 0)')
    parser.add_argument('--bg-color', nargs=3, type=int, default=[255, 255, 255],
                       help='背景颜色 RGB值 (默认: 255 255 255)')
    
    args = parser.parse_args()
    
    # 如果没有提供图片参数，使用内置数组
    if not args.images:
        print("使用内置图片数组:")
        for i, img_path in enumerate(IMAGE_FILES):
            print(f"  {i+1}. {img_path}")
        images_to_process = IMAGE_FILES
    else:
        images_to_process = args.images
    
    print("=" * 60)
    print("图片拼接工具")
    print("=" * 60)
    
    # 验证背景颜色
    bg_color = tuple(args.bg_color)
    if len(bg_color) != 3 or any(c < 0 or c > 255 for c in bg_color):
        print("错误: 背景颜色必须是3个0-255之间的整数")
        return
    
    try:
        stitcher = ImageStitcher(
            images=images_to_process,
            output_path=args.output,
            direction=args.direction,
            spacing=args.spacing,
            background_color=bg_color
        )
        
        success = stitcher.stitch()
        
        if success:
            print(f"\n✓ 拼接成功！")
        else:
            print(f"\n✗ 拼接失败！")
            
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()