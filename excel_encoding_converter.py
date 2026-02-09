#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Excel Encoding Converter
Convert Mac-encoded Excel/CSV files to Windows-compatible encoding
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd
import chardet


def detect_encoding(file_path):
    """
    Detect the encoding of a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        Detected encoding name
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']


def convert_excel_encoding(input_path, output_path=None, force_encoding=None):
    """
    Convert Excel file encoding from Mac to Windows
    
    Args:
        input_path: Path to input Excel/CSV file
        output_path: Path to output file (default: adds '_win' suffix)
        force_encoding: Force specific input encoding (optional)
        
    Returns:
        Path to the converted file
    """
    input_path = Path(input_path)
    
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_win{input_path.suffix}"
    else:
        output_path = Path(output_path)
    
    file_extension = input_path.suffix.lower()
    
    print(f"Processing: {input_path}")
    print(f"File type: {file_extension}")
    
    try:
        if file_extension in ['.xlsx', '.xls']:
            # Handle Excel files
            print("Reading Excel file...")
            
            # Try different engines for reading
            try:
                df = pd.read_excel(input_path, engine='openpyxl')
            except Exception as e:
                print(f"Failed with openpyxl, trying xlrd... ({e})")
                df = pd.read_excel(input_path, engine='xlrd')
            
            print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Determine output format based on output file extension
            output_ext = output_path.suffix.lower()
            if output_ext == '.csv':
                # Save as CSV with Windows-compatible encoding
                print(f"Saving to CSV: {output_path}")
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                print("✓ Excel file converted to CSV successfully (UTF-8 with BOM)")
            else:
                # Save as Excel with Windows-compatible encoding
                print(f"Saving to Excel: {output_path}")
                df.to_excel(output_path, index=False, engine='openpyxl')
                print("✓ Excel file converted successfully")
            
        elif file_extension == '.csv':
            # Handle CSV files - this is where encoding issues are most common
            print("Reading CSV file...")
            
            # Detect or use forced encoding
            if force_encoding:
                input_encoding = force_encoding
                print(f"Using forced encoding: {input_encoding}")
            else:
                input_encoding = detect_encoding(input_path)
                print(f"Detected encoding: {input_encoding}")
            
            # Common Mac encodings: 'mac_roman', 'utf-8', 'latin1', 'iso-8859-1'
            # Try to read with detected encoding
            try:
                df = pd.read_csv(input_path, encoding=input_encoding)
            except Exception as e:
                print(f"Failed with {input_encoding}, trying UTF-8...")
                try:
                    df = pd.read_csv(input_path, encoding='utf-8')
                except:
                    print(f"Failed with UTF-8, trying latin1...")
                    df = pd.read_csv(input_path, encoding='latin1')
            
            print(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            
            # Determine output format
            if output_path.suffix.lower() == '.csv':
                # Save as CSV with Windows-compatible encoding (UTF-8 with BOM or GB18030)
                print(f"Saving to CSV: {output_path}")
                df.to_csv(output_path, index=False, encoding='utf-8-sig')  # UTF-8 with BOM for Windows Excel
                print("✓ CSV file converted successfully (UTF-8 with BOM)")
            else:
                # Save as Excel
                print(f"Saving to Excel: {output_path}")
                df.to_excel(output_path, index=False, engine='openpyxl')
                print("✓ CSV converted to Excel successfully")
        
        else:
            raise ValueError(f"Unsupported file format: {file_extension}. Supported: .xlsx, .xls, .csv")
        
        print(f"\n{'='*60}")
        print(f"Conversion complete!")
        print(f"Input:  {input_path}")
        print(f"Output: {output_path}")
        print(f"{'='*60}\n")
        
        return str(output_path)
    
    except Exception as e:
        print(f"\n✗ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return None


def batch_convert(input_dir, output_dir=None, file_pattern='*'):
    """
    Batch convert Excel/CSV files in a directory
    
    Args:
        input_dir: Directory containing files to convert
        output_dir: Output directory (default: input_dir/converted)
        file_pattern: File pattern to match (default: all files)
        
    Returns:
        Dictionary of conversion results
    """
    input_dir = Path(input_dir)
    
    if not input_dir.exists():
        raise FileNotFoundError(f"Directory not found: {input_dir}")
    
    if output_dir is None:
        output_dir = input_dir / 'converted'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(exist_ok=True, parents=True)
    
    # Find all Excel and CSV files
    extensions = ['.xlsx', '.xls', '.csv']
    files = []
    
    for ext in extensions:
        files.extend(input_dir.glob(f'{file_pattern}{ext}'))
    
    if not files:
        print(f"No Excel or CSV files found in: {input_dir}")
        return {}
    
    print(f"Found {len(files)} file(s) to convert\n")
    print("="*60)
    
    results = {}
    success_count = 0
    
    for file_path in files:
        output_path = output_dir / f"{file_path.stem}_win{file_path.suffix}"
        
        try:
            result = convert_excel_encoding(file_path, output_path)
            results[str(file_path)] = result
            if result:
                success_count += 1
            print()
        except Exception as e:
            print(f"✗ Failed to convert {file_path}: {e}\n")
            results[str(file_path)] = None
    
    print("="*60)
    print(f"Batch conversion complete!")
    print(f"Successfully converted: {success_count}/{len(files)} file(s)")
    print(f"Output directory: {output_dir}")
    print("="*60)
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Convert Mac-encoded Excel/CSV files to Windows-compatible encoding',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert single file
  python excel_encoding_converter.py input.xlsx
  
  # Convert single file with specific output path
  python excel_encoding_converter.py input.xlsx -o output.xlsx
  
  # Convert CSV with forced encoding
  python excel_encoding_converter.py input.csv -e mac_roman
  
  # Batch convert all files in directory
  python excel_encoding_converter.py /path/to/directory -b
  
  # Batch convert with custom output directory
  python excel_encoding_converter.py /path/to/directory -b -o /path/to/output
        """
    )
    
    parser.add_argument('input', help='Input file or directory path')
    parser.add_argument('-o', '--output', help='Output file or directory path')
    parser.add_argument('-b', '--batch', action='store_true', help='Batch mode: convert all files in directory')
    parser.add_argument('-e', '--encoding', help='Force specific input encoding (e.g., mac_roman, utf-8, latin1)')
    parser.add_argument('-p', '--pattern', default='*', help='File pattern for batch mode (default: *)')
    
    args = parser.parse_args()
    
    try:
        if args.batch:
            # Batch mode
            batch_convert(args.input, args.output, args.pattern)
        else:
            # Single file mode
            convert_excel_encoding(args.input, args.output, args.encoding)
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
