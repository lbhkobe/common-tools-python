from pypdf import PdfReader, PdfWriter
import os


def split_pdf_by_page_range(input_path, output_dir, page_ranges):
    """
    Split PDF into multiple files based on page ranges.
    
    Args:
        input_path: Path to input PDF file
        output_dir: Directory to save split PDFs
        page_ranges: List of tuples (start, end) for page ranges (1-based indexing)
                    Example: [(1, 5), (6, 10), (11, 15)]
    """
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        print(f"Total pages in PDF: {total_pages}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        for idx, (start, end) in enumerate(page_ranges, 1):
            # Validate page range
            if start < 1 or end > total_pages or start > end:
                print(f"Warning: Invalid range ({start}-{end}), skipping...")
                continue
            
            writer = PdfWriter()
            
            # Add pages (convert to 0-based index)
            for page_num in range(start - 1, end):
                writer.add_page(reader.pages[page_num])
            
            # Save split PDF
            output_path = os.path.join(output_dir, f"{base_name}_part{idx}_pages{start}-{end}.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"Created: {output_path} (pages {start}-{end})")
        
        print(f"\nSuccessfully split PDF into {len(page_ranges)} files")
    
    except FileNotFoundError:
        print(f"Error: File not found - {input_path}")
    except Exception as e:
        print(f"Error splitting PDF: {str(e)}")


def split_pdf_by_page_numbers(input_path, output_dir, page_numbers):
    """
    Split PDF by extracting specific page numbers into separate files.
    
    Args:
        input_path: Path to input PDF file
        output_dir: Directory to save split PDFs
        page_numbers: List of page numbers to extract (1-based indexing)
                     Example: [1, 3, 5, 7]
    """
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        print(f"Total pages in PDF: {total_pages}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        for page_num in page_numbers:
            # Validate page number
            if page_num < 1 or page_num > total_pages:
                print(f"Warning: Page {page_num} out of range, skipping...")
                continue
            
            writer = PdfWriter()
            writer.add_page(reader.pages[page_num - 1])  # Convert to 0-based index
            
            # Save single page PDF
            output_path = os.path.join(output_dir, f"{base_name}_page{page_num}.pdf")
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"Created: {output_path}")
        
        print(f"\nSuccessfully extracted {len(page_numbers)} pages")
    
    except FileNotFoundError:
        print(f"Error: File not found - {input_path}")
    except Exception as e:
        print(f"Error splitting PDF: {str(e)}")


def split_pdf_every_n_pages(input_path, output_dir, pages_per_file):
    """
    Split PDF into multiple files with N pages each.
    
    Args:
        input_path: Path to input PDF file
        output_dir: Directory to save split PDFs
        pages_per_file: Number of pages per output file
    """
    try:
        reader = PdfReader(input_path)
        total_pages = len(reader.pages)
        
        print(f"Total pages in PDF: {total_pages}")
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.splitext(os.path.basename(input_path))[0]
        
        file_count = 0
        
        for start_page in range(0, total_pages, pages_per_file):
            end_page = min(start_page + pages_per_file, total_pages)
            
            writer = PdfWriter()
            
            for page_num in range(start_page, end_page):
                writer.add_page(reader.pages[page_num])
            
            file_count += 1
            output_path = os.path.join(output_dir, f"{base_name}_part{file_count}.pdf")
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            print(f"Created: {output_path} (pages {start_page + 1}-{end_page})")
        
        print(f"\nSuccessfully split PDF into {file_count} files")
    
    except FileNotFoundError:
        print(f"Error: File not found - {input_path}")
    except Exception as e:
        print(f"Error splitting PDF: {str(e)}")


if __name__ == "__main__":
    # Example usage - modify these parameters
    input_pdf = "D:\\ChromeDownload\\merged_output1-12-page.pdf"
    output_directory = "D:\\ChromeDownload\\split_pdfs"
    
    print("=" * 60)
    print("PDF Splitter")
    print("=" * 60)
    
    # Method 1: Split by page ranges
    print("\n1. Split by page ranges:")
    page_ranges = [(1, 171), (172, 201)]  # Modify these ranges
    split_pdf_by_page_range(input_pdf, output_directory, page_ranges)
    
    # Method 2: Extract specific pages
    #print("\n2. Extract specific pages:")
   # specific_pages = [1, 3, 5, 7, 9]  # Modify these page numbers
    # split_pdf_by_page_numbers(input_pdf, output_directory, specific_pages)
    
    # Method 3: Split every N pages
    #print("\n3. Split every N pages:")
    #pages_per_file = 5  # Modify this number
    # split_pdf_every_n_pages(input_pdf, output_directory, pages_per_file)
    
    print("\nUncomment the method you want to use and run the script.")
