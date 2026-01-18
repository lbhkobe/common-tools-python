from pypdf import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def add_page_number(page, page_num):
    """
    Add page number to a PDF page.
    
    Args:
        page: PDF page object
        page_num: Page number to add
    """
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    
    # Get page dimensions
    page_width = float(page.mediabox.width)
    page_height = float(page.mediabox.height)
    
    # Add page number at bottom center
    can.setFont('Helvetica', 10)
    can.drawCentredString(page_width / 2, 20, str(page_num))
    can.save()
    
    packet.seek(0)
    number_pdf = PdfReader(packet)
    page.merge_page(number_pdf.pages[0])
    return page


def merge_pdfs(pdf_paths, output_path, add_numbers=False):
    """
    Merge multiple PDF files into one with sequential page numbers.
    
    Args:
        pdf_paths: List of paths to PDF files to merge
        output_path: Path for the merged output PDF file
        add_numbers: Whether to add sequential page numbers (default: True)
    """
    writer = PdfWriter()
    
    try:
        page_counter = 1
        
        # Read and append pages from each PDF
        for pdf_path in pdf_paths:
            reader = PdfReader(pdf_path)
            for page in reader.pages:
                if add_numbers:
                    page = add_page_number(page, page_counter)
                writer.add_page(page)
                page_counter += 1
            print(f"Added: {pdf_path}")
        
        # Write the merged PDF to output file
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        print(f"\nSuccessfully merged {len(pdf_paths)} PDFs into: {output_path}")
        print(f"Total pages: {page_counter - 1}")
        
    except FileNotFoundError as e:
        print(f"Error: PDF file not found - {e}")
    except Exception as e:
        print(f"Error merging PDFs: {e}")


if __name__ == "__main__":
    # Example usage - modify these paths for your files
    pdf_files = [
        "E:\\QLDownload\\1-11.pdf",
        "E:\\QLDownload\\12.pdf"
        # Add more PDF files as needed
    ]
    output = "E:\\QLDownload\\merged_output1-12-page.pdf"
    
    merge_pdfs(pdf_files, output)
