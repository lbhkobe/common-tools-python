import pdfplumber
import pandas as pd
import os
from pathlib import Path


def extract_tables_from_pdf(pdf_path, output_dir=None):
    """
    Extract all tables from PDF and combine them in one Excel file with single sheet.
    All tables are appended without repeating headers (assuming same structure).
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save extracted tables (default: same as PDF)
    
    Returns:
        Path to the created Excel file
    """
    print(f"\n[DEBUG] 开始处理PDF文件: {pdf_path}")
    print(f"[DEBUG] 检查文件是否存在: {os.path.exists(pdf_path)}")
    
    if output_dir is None:
        output_dir = os.path.dirname(pdf_path)
    
    print(f"[DEBUG] 输出目录: {output_dir}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_name = Path(pdf_path).stem
    output_filename = f"{pdf_name}_tables.xlsx"
    output_path = os.path.join(output_dir, output_filename)
    
    print(f"[DEBUG] 目标Excel文件路径: {output_path}")
    
    try:
        print(f"[DEBUG] 尝试打开PDF文件...")
        with pdfplumber.open(pdf_path) as pdf:
            total_tables = 0
            all_rows = []
            
            # Fixed header - 17 columns as specified by user
            header = ['账号', '交易时间', '借方发生额', '贷方发生额', '余额', '币种', 
                     '对方户名', '对方账号', '对方开户机构', '记账日期', '摘要', '备注',
                     '账户明细编号-交易流水号', '企业流水号', '凭证种类', '凭证号', '交易介质编号']
            
            print(f"[DEBUG] 使用固定表头（共{len(header)}列）: {header}")
            
            print(f"Processing PDF: {pdf_path}")
            print(f"Total pages: {len(pdf.pages)}\n")
            
            for page_num, page in enumerate(pdf.pages, start=1):
                print(f"[DEBUG] 处理第 {page_num} 页...")
                # Extract tables from the page
                tables = page.extract_tables()
                print(f"[DEBUG] 第 {page_num} 页找到 {len(tables) if tables else 0} 个表格")
                
                if tables:
                    print(f"Page {page_num}: Found {len(tables)} table(s)")
                    
                    for table_num, table in enumerate(tables, start=1):
                        print(f"[DEBUG] 处理表格 {table_num}, 行数: {len(table) if table else 0}")
                        total_tables += 1
                        
                        if table and len(table) > 1:  # Need at least header + 1 data row
                            # Skip the first row (header row in PDF) and process data rows
                            for row in table[1:]:
                                print(f"[DEBUG] 原始行数据列数: {len(row)}")
                                # Adjust row to match header length (17 columns)
                                if len(row) < len(header):
                                    # Pad with empty string if row is shorter
                                    row = row + [''] * (len(header) - len(row))
                                    print(f"[DEBUG] 补齐后列数: {len(row)}")
                                elif len(row) > len(header):
                                    # Truncate if row is longer
                                    print(f"[DEBUG] 截断前列数: {len(row)}")
                                    row = row[:len(header)]
                                    print(f"[DEBUG] 截断后列数: {len(row)}")
                                
                                all_rows.append(row)
                            
                            print(f"  ✓ Added table {table_num} ({len(table)-1} rows)")
                else:
                    print(f"Page {page_num}: No tables found")
            
            print(f"\n[DEBUG] 处理完成，开始生成Excel...")
            print(f"[DEBUG] 使用固定表头（共{len(header)}列）")
            print(f"[DEBUG] 数据行数: {len(all_rows)}")
            
            if header and all_rows:
                print(f"[DEBUG] 创建DataFrame...")
                # Create single DataFrame with all data
                df = pd.DataFrame(all_rows, columns=header)
                
                print(f"[DEBUG] 保存到Excel文件: {output_path}")
                # Save to Excel
                df.to_excel(output_path, index=False, engine='openpyxl')
                print(f"[DEBUG] Excel文件保存成功！")
                
                print(f"\n{'='*60}")
                print(f"Extraction complete!")
                print(f"Total tables merged: {total_tables}")
                print(f"Total data rows: {len(df)}")
                print(f"Output file: {output_path}")
                print(f"{'='*60}")
                
                return output_path
            else:
                print(f"\n[DEBUG] 未找到表格或数据为空")
                print(f"No tables found in the PDF.")
                return None
            
    except FileNotFoundError as e:
        print(f"[DEBUG] 文件未找到异常: {e}")
        print(f"Error: PDF file not found - {pdf_path}")
        return None
    except Exception as e:
        print(f"[DEBUG] 发生异常: {type(e).__name__}")
        print(f"[DEBUG] 异常详情: {e}")
        import traceback
        print(f"[DEBUG] 完整错误堆栈:\n{traceback.format_exc()}")
        print(f"Error extracting tables: {e}")
        return None


def extract_all_text_from_pdf(pdf_path, output_path=None):
    """
    Extract all text content from PDF.
    
    Args:
        pdf_path: Path to the PDF file
        output_path: Path to save the text file (default: same name as PDF)
    
    Returns:
        Path to the created text file
    """
    if output_path is None:
        output_path = pdf_path.replace('.pdf', '_text.txt')
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            all_text = []
            
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text:
                    all_text.append(f"{'='*60}\n")
                    all_text.append(f"Page {page_num}\n")
                    all_text.append(f"{'='*60}\n")
                    all_text.append(text)
                    all_text.append("\n\n")
            
            # Save to text file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(all_text)
            
            print(f"Text extracted to: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


def batch_extract_tables(pdf_dir, output_dir=None):
    """
    Batch extract tables from all PDFs in a directory.
    
    Args:
        pdf_dir: Directory containing PDF files
        output_dir: Directory to save extracted tables (default: pdf_dir/extracted_tables)
    
    Returns:
        Dictionary mapping PDF paths to their extracted Excel file
    """
    if output_dir is None:
        output_dir = os.path.join(pdf_dir, 'extracted_tables')
    
    os.makedirs(output_dir, exist_ok=True)
    
    pdf_files = list(Path(pdf_dir).glob('*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in: {pdf_dir}")
        return {}
    
    results = {}
    
    print(f"Found {len(pdf_files)} PDF file(s)\n")
    
    for pdf_path in pdf_files:
        print(f"\n{'#'*60}")
        excel_file = extract_tables_from_pdf(str(pdf_path), output_dir)
        results[str(pdf_path)] = excel_file
    
    print(f"\n{'#'*60}")
    print(f"Batch extraction complete!")
    print(f"Processed {len(pdf_files)} PDF file(s)")
    print(f"Output directory: {output_dir}")
    
    return results


if __name__ == "__main__":
    # Example 1: Extract tables from a single PDF
    pdf_file = "E:\\QLDownload\\1-11.pdf"
    
    # Extract tables to Excel files
    extract_tables_from_pdf(pdf_file)
    
    # Example 2: Extract all text content
    # extract_all_text_from_pdf(pdf_file)
    
    # Example 3: Batch extract from multiple PDFs
    # pdf_directory = "D:\\ChromeDownload"
    # batch_extract_tables(pdf_directory)
