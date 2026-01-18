import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from datetime import datetime


class ExcelComparatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel对比器")
        self.root.geometry("900x700")
        
        self.file1_path = ""
        self.file2_path = ""
        self.df1 = None
        self.df2 = None
        self.key_columns = []
        
        self.setup_ui()
    
    def setup_ui(self):
        # 标题
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=60)
        title_frame.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(title_frame, text="Excel 数据对比工具", 
                font=("微软雅黑", 16, "bold"), bg="#2c3e50", fg="white").pack(pady=15)
        
        # 主容器
        main_frame = tk.Frame(self.root, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 文件选择区域
        file_frame = tk.LabelFrame(main_frame, text="选择Excel文件", 
                                   font=("微软雅黑", 11, "bold"), bg="#ecf0f1", padx=10, pady=10)
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 文件1
        file1_frame = tk.Frame(file_frame, bg="#ecf0f1")
        file1_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(file1_frame, text="文件1:", font=("微软雅黑", 10), bg="#ecf0f1", width=8).pack(side=tk.LEFT)
        self.file1_entry = tk.Entry(file1_frame, font=("微软雅黑", 9), width=60)
        self.file1_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(file1_frame, text="浏览", command=lambda: self.browse_file(1),
                 bg="#3498db", fg="white", font=("微软雅黑", 9)).pack(side=tk.LEFT)
        
        # 文件2
        file2_frame = tk.Frame(file_frame, bg="#ecf0f1")
        file2_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(file2_frame, text="文件2:", font=("微软雅黑", 10), bg="#ecf0f1", width=8).pack(side=tk.LEFT)
        self.file2_entry = tk.Entry(file2_frame, font=("微软雅黑", 9), width=60)
        self.file2_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(file2_frame, text="浏览", command=lambda: self.browse_file(2),
                 bg="#3498db", fg="white", font=("微软雅黑", 9)).pack(side=tk.LEFT)
        
        # 加载按钮
        tk.Button(file_frame, text="加载文件", command=self.load_files,
                 bg="#27ae60", fg="white", font=("微软雅黑", 10, "bold"), 
                 padx=20, pady=5).pack(pady=10)
        
        # 列选择区域
        column_frame = tk.LabelFrame(main_frame, text="选择唯一标识列（用于匹配）", 
                                     font=("微软雅黑", 11, "bold"), bg="#ecf0f1", padx=10, pady=10)
        column_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(column_frame, text="从下方列表中选择一个或多个列作为唯一标识（组合后唯一）：",
                font=("微软雅黑", 9), bg="#ecf0f1").pack(pady=5)
        
        # 列列表
        list_frame = tk.Frame(column_frame, bg="#ecf0f1")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.column_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE,
                                         font=("微软雅黑", 9), height=10,
                                         yscrollcommand=scrollbar.set)
        self.column_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.column_listbox.yview)
        
        # 按钮区域
        button_frame = tk.Frame(main_frame, bg="#ecf0f1")
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(button_frame, text="开始对比", command=self.compare_files,
                 bg="#e74c3c", fg="white", font=("微软雅黑", 11, "bold"),
                 padx=30, pady=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="清空", command=self.clear_all,
                 bg="#95a5a6", fg="white", font=("微软雅黑", 11, "bold"),
                 padx=30, pady=10).pack(side=tk.LEFT, padx=5)
        
        # 状态栏
        self.status_label = tk.Label(self.root, text="就绪", bg="#34495e", fg="white",
                                     font=("微软雅黑", 9), anchor=tk.W, padx=10)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def browse_file(self, file_num):
        """浏览并选择Excel文件"""
        file_path = filedialog.askopenfilename(
            title=f"选择Excel文件 {file_num}",
            filetypes=[("Excel文件", "*.xlsx *.xls"), ("所有文件", "*.*")]
        )
        
        if file_path:
            if file_num == 1:
                self.file1_entry.delete(0, tk.END)
                self.file1_entry.insert(0, file_path)
                self.file1_path = file_path
            else:
                self.file2_entry.delete(0, tk.END)
                self.file2_entry.insert(0, file_path)
                self.file2_path = file_path
    
    def load_files(self):
        """加载两个Excel文件"""
        if not self.file1_path or not self.file2_path:
            messagebox.showwarning("警告", "请先选择两个Excel文件")
            return
        
        try:
            self.status_label.config(text="正在加载文件...")
            self.root.update()
            
            # 读取Excel文件
            self.df1 = pd.read_excel(self.file1_path)
            self.df2 = pd.read_excel(self.file2_path)
            
            # 检查列是否一致
            cols1 = set(self.df1.columns)
            cols2 = set(self.df2.columns)
            
            if cols1 != cols2:
                missing_in_1 = cols2 - cols1
                missing_in_2 = cols1 - cols2
                msg = "两个文件的列不完全一致：\n"
                if missing_in_1:
                    msg += f"文件1缺少的列: {', '.join(missing_in_1)}\n"
                if missing_in_2:
                    msg += f"文件2缺少的列: {', '.join(missing_in_2)}\n"
                msg += "\n将只对比共同的列。是否继续？"
                
                if not messagebox.askyesno("列不匹配", msg):
                    return
            
            # 更新列列表
            self.column_listbox.delete(0, tk.END)
            common_columns = sorted(list(cols1 & cols2))
            
            for col in common_columns:
                self.column_listbox.insert(tk.END, col)
            
            self.status_label.config(text=f"文件加载成功 | 文件1: {len(self.df1)}行, 文件2: {len(self.df2)}行")
            messagebox.showinfo("成功", 
                              f"文件加载成功！\n\n文件1: {len(self.df1)}行 × {len(self.df1.columns)}列\n" +
                              f"文件2: {len(self.df2)}行 × {len(self.df2.columns)}列\n\n" +
                              f"请选择唯一标识列，然后点击'开始对比'")
        
        except Exception as e:
            self.status_label.config(text="加载失败")
            messagebox.showerror("错误", f"加载文件失败：\n{str(e)}")
    
    def compare_files(self):
        """对比两个Excel文件"""
        if self.df1 is None or self.df2 is None:
            messagebox.showwarning("警告", "请先加载两个Excel文件")
            return
        
        # 获取选中的列
        selected_indices = self.column_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("警告", "请至少选择一个唯一标识列")
            return
        
        self.key_columns = [self.column_listbox.get(i) for i in selected_indices]
        
        try:
            self.status_label.config(text="正在对比数据...")
            self.root.update()
            
            # 执行对比
            result = self.perform_comparison()
            
            # 保存结果
            output_path = self.save_comparison_result(result)
            
            self.status_label.config(text="对比完成")
            messagebox.showinfo("完成", 
                              f"对比完成！\n\n" +
                              f"匹配的记录: {result['matched']}条\n" +
                              f"文件1独有: {result['only_in_1']}条\n" +
                              f"文件2独有: {result['only_in_2']}条\n" +
                              f"有差异的记录: {result['differences']}条\n\n" +
                              f"结果已保存至:\n{output_path}")
        
        except Exception as e:
            self.status_label.config(text="对比失败")
            messagebox.showerror("错误", f"对比失败：\n{str(e)}")
    
    def perform_comparison(self):
        """执行数据对比"""
        # 创建唯一标识列
        df1 = self.df1.copy()
        df2 = self.df2.copy()
        
        # 生成组合键
        df1['_key_'] = df1[self.key_columns].astype(str).agg('||'.join, axis=1)
        df2['_key_'] = df2[self.key_columns].astype(str).agg('||'.join, axis=1)
        
        # 找出匹配和不匹配的记录
        keys1 = set(df1['_key_'])
        keys2 = set(df2['_key_'])
        
        common_keys = keys1 & keys2
        only_in_1_keys = keys1 - keys2
        only_in_2_keys = keys2 - keys1
        
        # 提取数据
        only_in_1 = df1[df1['_key_'].isin(only_in_1_keys)].drop('_key_', axis=1)
        only_in_2 = df2[df2['_key_'].isin(only_in_2_keys)].drop('_key_', axis=1)
        
        # 对比共同记录的差异
        differences = []
        common_columns = [col for col in df1.columns if col in df2.columns and col != '_key_']
        
        for key in common_keys:
            row1 = df1[df1['_key_'] == key].iloc[0]
            row2 = df2[df2['_key_'] == key].iloc[0]
            
            diff_found = False
            diff_details = {}
            
            for col in common_columns:
                val1 = row1[col]
                val2 = row2[col]
                
                # 处理NaN值
                if pd.isna(val1) and pd.isna(val2):
                    continue
                
                if pd.isna(val1) or pd.isna(val2) or val1 != val2:
                    diff_found = True
                    diff_details[col] = (val1, val2)
            
            if diff_found:
                diff_row = {}
                for col in self.key_columns:
                    diff_row[col] = row1[col]
                
                for col, (v1, v2) in diff_details.items():
                    diff_row[f'{col}_文件1'] = v1
                    diff_row[f'{col}_文件2'] = v2
                    diff_row[f'{col}_差异'] = '不同' if v1 != v2 else ''
                
                differences.append(diff_row)
        
        differences_df = pd.DataFrame(differences) if differences else pd.DataFrame()
        
        return {
            'matched': len(common_keys),
            'only_in_1': len(only_in_1_keys),
            'only_in_2': len(only_in_2_keys),
            'differences': len(differences),
            'only_in_1_data': only_in_1,
            'only_in_2_data': only_in_2,
            'differences_data': differences_df
        }
    
    def save_comparison_result(self, result):
        """保存对比结果到Excel"""
        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.dirname(self.file1_path)
        output_path = os.path.join(output_dir, f"对比结果_{timestamp}.xlsx")
        
        # 创建Excel写入器
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # 汇总页
            summary_data = {
                '项目': ['文件1路径', '文件2路径', '唯一标识列', '文件1总行数', '文件2总行数', 
                       '匹配的记录数', '文件1独有记录', '文件2独有记录', '有差异的记录'],
                '值': [
                    self.file1_path,
                    self.file2_path,
                    ', '.join(self.key_columns),
                    len(self.df1),
                    len(self.df2),
                    result['matched'],
                    result['only_in_1'],
                    result['only_in_2'],
                    result['differences']
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='汇总', index=False)
            
            # 差异详情页
            if not result['differences_data'].empty:
                result['differences_data'].to_excel(writer, sheet_name='差异详情', index=False)
            
            # 文件1独有记录
            if not result['only_in_1_data'].empty:
                result['only_in_1_data'].to_excel(writer, sheet_name='仅文件1有', index=False)
            
            # 文件2独有记录
            if not result['only_in_2_data'].empty:
                result['only_in_2_data'].to_excel(writer, sheet_name='仅文件2有', index=False)
        
        return output_path
    
    def clear_all(self):
        """清空所有选择"""
        self.file1_entry.delete(0, tk.END)
        self.file2_entry.delete(0, tk.END)
        self.file1_path = ""
        self.file2_path = ""
        self.df1 = None
        self.df2 = None
        self.column_listbox.delete(0, tk.END)
        self.status_label.config(text="已清空")


def main():
    root = tk.Tk()
    app = ExcelComparatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
