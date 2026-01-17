"""
M3U8 视频下载器
支持下载和合并 m3u8 视频流
"""

import os
import re
import requests
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from pathlib import Path


class M3U8Downloader:
    """M3U8 下载器类"""
    
    def __init__(self, m3u8_url, output_dir="downloads", max_workers=10):
        """
        初始化下载器
        
        Args:
            m3u8_url: m3u8 文件 URL
            output_dir: 输出目录
            max_workers: 最大并发下载数
        """
        self.m3u8_url = m3u8_url
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.segments = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def parse_m3u8(self):
        """解析 m3u8 文件，获取所有视频片段 URL"""
        try:
            print(f"正在解析 m3u8 文件: {self.m3u8_url}")
            response = self.session.get(self.m3u8_url, timeout=30)
            response.raise_for_status()
            
            content = response.text
            lines = content.split('\n')
            
            base_url = self._get_base_url(self.m3u8_url)
            
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#'):
                    segment_url = urljoin(base_url, line)
                    self.segments.append(segment_url)
            
            print(f"解析完成，共找到 {len(self.segments)} 个视频片段")
            return True
            
        except Exception as e:
            print(f"解析 m3u8 文件失败: {str(e)}")
            return False
    
    def _get_base_url(self, url):
        """获取基础 URL"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{os.path.dirname(parsed.path)}/"
    
    def download_segment(self, segment_url, index):
        """
        下载单个视频片段
        
        Args:
            segment_url: 片段 URL
            index: 片段索引
            
        Returns:
            tuple: (index, success, file_path)
        """
        try:
            filename = f"segment_{index:06d}.ts"
            file_path = self.output_dir / filename
            
            if file_path.exists():
                return (index, True, str(file_path))
            
            response = self.session.get(segment_url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            return (index, True, str(file_path))
            
        except Exception as e:
            print(f"下载片段 {index} 失败: {str(e)}")
            return (index, False, None)
    
    def download_all_segments(self):
        """下载所有视频片段"""
        if not self.segments:
            print("没有找到视频片段")
            return False
        
        print(f"开始下载 {len(self.segments)} 个视频片段...")
        
        downloaded_files = {}
        failed_segments = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.download_segment, url, i): i
                for i, url in enumerate(self.segments)
            }
            
            completed = 0
            for future in as_completed(futures):
                index, success, file_path = future.result()
                
                if success:
                    downloaded_files[index] = file_path
                else:
                    failed_segments.append(index)
                
                completed += 1
                progress = (completed / len(self.segments)) * 100
                print(f"\r下载进度: {progress:.1f}% ({completed}/{len(self.segments)})", end='', flush=True)
        
        print()
        
        if failed_segments:
            print(f"警告: {len(failed_segments)} 个片段下载失败")
            print(f"失败的片段索引: {failed_segments}")
        
        print(f"成功下载 {len(downloaded_files)} 个片段")
        return len(downloaded_files) > 0
    
    def merge_segments(self, output_filename="output.mp4"):
        """
        合并所有视频片段
        
        Args:
            output_filename: 输出文件名
            
        Returns:
            bool: 是否合并成功
        """
        try:
            output_path = self.output_dir / output_filename
            
            print(f"正在合并视频片段到: {output_path}")
            
            segment_files = sorted(self.output_dir.glob("segment_*.ts"))
            
            if not segment_files:
                print("没有找到视频片段文件")
                return False
            
            with open(output_path, 'wb') as outfile:
                for segment_file in segment_files:
                    with open(segment_file, 'rb') as infile:
                        outfile.write(infile.read())
            
            print(f"合并完成: {output_path}")
            print(f"文件大小: {output_path.stat().st_size / (1024 * 1024):.2f} MB")
            
            return True
            
        except Exception as e:
            print(f"合并视频片段失败: {str(e)}")
            return False
    
    def cleanup(self):
        """清理临时文件"""
        try:
            segment_files = self.output_dir.glob("segment_*.ts")
            for file in segment_files:
                file.unlink()
            print("临时文件已清理")
        except Exception as e:
            print(f"清理临时文件失败: {str(e)}")
    
    def download(self, output_filename="output.mp4", cleanup=True):
        """
        执行完整的下载流程
        
        Args:
            output_filename: 输出文件名
            cleanup: 是否清理临时文件
            
        Returns:
            bool: 是否下载成功
        """
        try:
            if not self.parse_m3u8():
                return False
            
            if not self.download_all_segments():
                return False
            
            if not self.merge_segments(output_filename):
                return False
            
            if cleanup:
                self.cleanup()
            
            print("\n下载完成！")
            return True
            
        except Exception as e:
            print(f"\n下载过程出错: {str(e)}")
            return False


def main():
    """主函数"""
    print("=" * 60)
    print("M3U8 视频下载器")
    print("=" * 60)
    
    builtin_urls = {
        "1": {
            "name": "大语言模型基础通识",
            "url": "https://vod-cdn-hedu.hisense.com/encrypted/rendition/1/172208175/202511/b8b367975a113ab210f154371d29df29_1762321128553-3000k1762321487497.m3u8?wsSecret=5a879e4726647e24d7ef7e9c4c59d4cd&wsTime=6968c884&keeptime=600"
        },
        "2": {
            "name": "多模态大模型通识",
            "url":"https://vod-cdn-hedu.hisense.com/encrypted/rendition/1/172208175/202511/f21e91b0b029b093b3d1a55ca8db2d7d_1762321172124-3000k1762321516466.m3u8?wsSecret=420d89cd7dc0f21973c316d7a6ddc81a&wsTime=6968ccb6&keeptime=600"
        },
        "3": {
            "name": "大模型选型推荐指南",
            "url":"https://vod-cdn-hedu.hisense.com/encrypted/rendition/1/172208175/202511/eb9dee7e02b127d29c94d8266a658be9_1762321203368-3000k1762321535050.m3u8?wsSecret=96976c18ecbe7502f441f87b77ac0e7e&wsTime=6968ce50&keeptime=600"
        },
        "4": {
            "name": "提示词工程开发及优化技巧",
            "url":"https://vod-cdn-hedu.hisense.com/encrypted/rendition/1/172208175/202511/e02427643ebba1b8ff7e8288b233108e_1762394474548-3000k1762394684448.m3u8?wsSecret=3b33844f610e78cb2f0e28e5a340f7e6&wsTime=6968ce85&keeptime=600"
        },
        "5": {
            "name": "智能体基础介绍",
            "url":"https://vod-cdn-hedu.hisense.com/encrypted/rendition/1/172208175/202511/f7bcf9b838050772f7532519de782fdc_1762394830785-3000k1762397083269.m3u8?wsSecret=6393c70feef5ba87417536d2d0de6a98&wsTime=6968ce9f&keeptime=600"
        },
        "6": {
            "name": "星海智能体平台介绍",
            "url":"https://vod-cdn-hedu.hisense.com/encrypted/rendition/1/172208175/202511/d9ea09adb1d7ce34fc202cb3f33def15_1762394788489-3000k1762397050083.m3u8?wsSecret=de0f4a4fbbaaca78d4f153e3866d18b5&wsTime=6968ceb5&keeptime=600"
        },
        "7" : {
            "name": "大模型应用进阶",
            "url":"https://vod-cdn-hedu.hisense.com/encrypted/rendition/1/172208175/202511/606fac0c2308f0270ae0b29227f018f5_1762752895332-3000k1762753007129.m3u8?wsSecret=69ceffdc9d8f69f6f10381101b0f4e46&wsTime=69699251&keeptime=600"
        },
        "8" : {
            "name": "RAG架构与实践指南v2",
            "url":"https://vod-cdn-hedu.hisense.com/encrypted/rendition/1/172208175/202511/b69ab05b095d726daa7f462a9482eaa6_1762397359498-3000k1762397742356.m3u8?wsSecret=c3bc116ca98192411da1e4a5aca8e6b4&wsTime=696992d1&keeptime=600"
        },
        "9" : {
            "name": "大模型应用进阶",
            "url":""
        },
        "10" : {
            "name": "大模型应用进阶",
            "url":""
        }

    }
    
    print("\n请选择输入方式:")
    print("1. 使用内置链接")
    print("2. 手动输入 URL")
    
    choice = input("\n请输入选项 (1/2, 默认 1): ").strip()
    
    m3u8_url = ""
    
    if choice == "2":
        m3u8_url = input("请输入 m3u8 URL: ").strip()
        default_filename = "output.mp4"
    else:
        print("\n内置链接列表:")
        for key, value in builtin_urls.items():
            print(f"{key}. {value['name']}")
        
        url_choice = input("\n请选择链接编号 (默认 1): ").strip()
        
        if url_choice in builtin_urls:
            selected = builtin_urls[url_choice]
            m3u8_url = selected['url']
            print(f"\n已选择: {selected['name']}")
        else:
            selected = builtin_urls["1"]
            m3u8_url = selected['url']
            print(f"\n使用默认: {selected['name']}")
        
        default_filename = f"{selected['name']}.mp4"
    
    print(f"\n下载链接: {m3u8_url}")
    
    output_dir = input("请输入输出目录 (直接回车使用默认): ").strip()
    if not output_dir:
        output_dir = "downloads"
    
    output_filename = input(f"请输入输出文件名 (直接回车使用默认: {default_filename}): ").strip()
    if not output_filename:
        output_filename = default_filename
    
    max_workers = input("请输入并发下载数 (直接回车使用默认 30): ").strip()
    if max_workers and max_workers.isdigit():
        max_workers = int(max_workers)
    else:
        max_workers = 30
    
    cleanup = input("下载完成后是否清理临时文件? (y/n, 默认 y): ").strip().lower()
    cleanup = cleanup != 'n'
    
    print("\n开始下载...")
    print("-" * 60)
    
    downloader = M3U8Downloader(m3u8_url, output_dir, max_workers)
    success = downloader.download(output_filename, cleanup)
    
    print("-" * 60)
    
    if success:
        print(f"✓ 下载成功！文件保存在: {Path(output_dir) / output_filename}")
    else:
        print("✗ 下载失败，请检查网络连接和 URL 是否正确")


if __name__ == "__main__":
    main()
