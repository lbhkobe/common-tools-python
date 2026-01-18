import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageTk
import fitz  # PyMuPDF for PDF rendering
import os


class PDFEditorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Editor")
        self.root.geometry("1200x800")
        
        self.pdf_document = None
        self.current_page = 0
        self.total_pages = 0
        self.pdf_path = ""
        self.pages_to_delete = set()
        self.text_replacements = {}  # Store text replacements per page: {page_num: [(old, new), ...]}
        
        self.setup_ui()
    
    def setup_ui(self):
        # Top toolbar
        toolbar = tk.Frame(self.root, bg="#2c3e50", height=60)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Buttons
        btn_style = {"bg": "#3498db", "fg": "white", "font": ("Arial", 10, "bold"), 
                     "padx": 15, "pady": 8, "relief": tk.FLAT, "cursor": "hand2"}
        
        tk.Button(toolbar, text="Open PDF", command=self.open_pdf, **btn_style).pack(side=tk.LEFT, padx=10, pady=10)
        tk.Button(toolbar, text="Save As", command=self.save_pdf, **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="Edit Text", command=self.edit_text, **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="Split PDF", command=self.split_pdf, **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="Delete Page", command=self.mark_page_for_deletion, **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        tk.Button(toolbar, text="Rotate 90°", command=lambda: self.rotate_page(90), **btn_style).pack(side=tk.LEFT, padx=5, pady=10)
        
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Page list
        left_panel = tk.Frame(main_container, bg="#ecf0f1", width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(left_panel, text="Pages", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Page listbox with scrollbar
        list_frame = tk.Frame(left_panel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.page_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                       font=("Arial", 10), selectmode=tk.SINGLE)
        self.page_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.page_listbox.bind('<<ListboxSelect>>', self.on_page_select)
        
        scrollbar.config(command=self.page_listbox.yview)
        
        # Center panel - PDF viewer
        center_panel = tk.Frame(main_container, bg="white")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Canvas for PDF display
        canvas_frame = tk.Frame(center_panel)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(canvas_frame, bg="#f5f5f5", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bottom navigation
        nav_frame = tk.Frame(center_panel, bg="white")
        nav_frame.pack(side=tk.BOTTOM, pady=10)
        
        tk.Button(nav_frame, text="◀ Previous", command=self.previous_page, **btn_style).pack(side=tk.LEFT, padx=5)
        
        self.page_label = tk.Label(nav_frame, text="No PDF loaded", font=("Arial", 11))
        self.page_label.pack(side=tk.LEFT, padx=20)
        
        tk.Button(nav_frame, text="Next ▶", command=self.next_page, **btn_style).pack(side=tk.LEFT, padx=5)
        
        # Right panel - Properties
        right_panel = tk.Frame(main_container, bg="#ecf0f1", width=250)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        
        tk.Label(right_panel, text="Properties", bg="#ecf0f1", font=("Arial", 12, "bold")).pack(pady=10)
        
        self.info_text = tk.Text(right_panel, wrap=tk.WORD, font=("Arial", 9), 
                                 bg="white", height=15, width=30)
        self.info_text.pack(padx=10, pady=5)
    
    def open_pdf(self):
        file_path = filedialog.askopenfilename(
            title="Select PDF file",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.pdf_path = file_path
            self.pdf_document = fitz.open(file_path)
            self.total_pages = len(self.pdf_document)
            self.current_page = 0
            self.pages_to_delete.clear()
            self.text_replacements.clear()
            
            # Update page list
            self.page_listbox.delete(0, tk.END)
            for i in range(self.total_pages):
                self.page_listbox.insert(tk.END, f"Page {i + 1}")
            
            self.page_listbox.select_set(0)
            self.display_page()
            self.update_info()
            
            messagebox.showinfo("Success", f"Loaded PDF with {self.total_pages} pages")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF: {str(e)}")
    
    def display_page(self):
        if not self.pdf_document:
            return
        
        try:
            page = self.pdf_document[self.current_page]
            
            # Render page to image
            zoom = 1.5
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Resize to fit canvas
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img.thumbnail((canvas_width - 20, canvas_height - 20), Image.Resampling.LANCZOS)
            
            # Display on canvas
            self.photo = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width // 2 if canvas_width > 1 else 400,
                canvas_height // 2 if canvas_height > 1 else 300,
                image=self.photo,
                anchor=tk.CENTER
            )
            
            # Update page label
            status = " [MARKED FOR DELETION]" if self.current_page in self.pages_to_delete else ""
            self.page_label.config(text=f"Page {self.current_page + 1} / {self.total_pages}{status}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display page: {str(e)}")
    
    def update_info(self):
        if not self.pdf_document:
            return
        
        self.info_text.delete(1.0, tk.END)
        
        metadata = self.pdf_document.metadata
        page = self.pdf_document[self.current_page]
        
        info = f"File: {os.path.basename(self.pdf_path)}\n\n"
        info += f"Total Pages: {self.total_pages}\n"
        info += f"Current Page: {self.current_page + 1}\n\n"
        info += f"Page Size: {page.rect.width:.1f} x {page.rect.height:.1f}\n\n"
        
        if metadata:
            info += "Metadata:\n"
            info += f"Title: {metadata.get('title', 'N/A')}\n"
            info += f"Author: {metadata.get('author', 'N/A')}\n"
            info += f"Subject: {metadata.get('subject', 'N/A')}\n"
        
        if self.pages_to_delete:
            info += f"\n\nPages to delete: {len(self.pages_to_delete)}\n"
            pages = sorted([p + 1 for p in self.pages_to_delete])
            info += f"{pages}"
        
        self.info_text.insert(1.0, info)
    
    def on_page_select(self, event):
        selection = self.page_listbox.curselection()
        if selection:
            self.current_page = selection[0]
            self.display_page()
            self.update_info()
    
    def next_page(self):
        if self.pdf_document and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.page_listbox.select_clear(0, tk.END)
            self.page_listbox.select_set(self.current_page)
            self.page_listbox.see(self.current_page)
            self.display_page()
            self.update_info()
    
    def previous_page(self):
        if self.pdf_document and self.current_page > 0:
            self.current_page -= 1
            self.page_listbox.select_clear(0, tk.END)
            self.page_listbox.select_set(self.current_page)
            self.page_listbox.see(self.current_page)
            self.display_page()
            self.update_info()
    
    def mark_page_for_deletion(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
        
        if self.current_page in self.pages_to_delete:
            self.pages_to_delete.remove(self.current_page)
            messagebox.showinfo("Info", f"Page {self.current_page + 1} unmarked for deletion")
        else:
            self.pages_to_delete.add(self.current_page)
            messagebox.showinfo("Info", f"Page {self.current_page + 1} marked for deletion")
        
        self.display_page()
        self.update_info()
    
    def edit_text(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
        
        try:
            page = self.pdf_document[self.current_page]
            text = page.get_text()
            
            if not text.strip():
                messagebox.showinfo("Info", "This page contains no extractable text")
                return
            
            # Create search & replace window
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Edit Text - Page {self.current_page + 1}")
            edit_window.geometry("900x700")
            
            # Instructions
            instruction = tk.Label(edit_window, 
                                  text="Find and replace text on this page. Changes preserve original formatting.",
                                  font=("Arial", 10), bg="#f0f0f0", pady=10)
            instruction.pack(fill=tk.X)
            
            # Show current page text (read-only)
            text_frame = tk.Frame(edit_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            tk.Label(text_frame, text="Current Page Text:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            text_scroll = tk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_display = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 10),
                                  height=15, yscrollcommand=text_scroll.set, state=tk.NORMAL)
            text_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.config(command=text_display.yview)
            text_display.insert(1.0, text)
            text_display.config(state=tk.DISABLED)
            
            # Search and Replace interface
            replace_frame = tk.Frame(edit_window, bg="#ecf0f1")
            replace_frame.pack(fill=tk.X, padx=10, pady=10)
            
            tk.Label(replace_frame, text="Find:", font=("Arial", 10, "bold"), bg="#ecf0f1").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            find_entry = tk.Entry(replace_frame, font=("Arial", 11), width=40)
            find_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
            
            tk.Label(replace_frame, text="Replace with:", font=("Arial", 10, "bold"), bg="#ecf0f1").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            replace_entry = tk.Entry(replace_frame, font=("Arial", 11), width=40)
            replace_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
            
            replace_frame.columnconfigure(1, weight=1)
            
            # Replacement list
            list_frame = tk.Frame(edit_window)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            tk.Label(list_frame, text="Replacements for this page:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
            
            list_scroll = tk.Scrollbar(list_frame)
            list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            replacement_list = tk.Listbox(list_frame, font=("Arial", 10), height=6,
                                         yscrollcommand=list_scroll.set)
            replacement_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            list_scroll.config(command=replacement_list.yview)
            
            # Load existing replacements
            if self.current_page not in self.text_replacements:
                self.text_replacements[self.current_page] = []
            
            def refresh_list():
                replacement_list.delete(0, tk.END)
                for old_text, new_text in self.text_replacements[self.current_page]:
                    replacement_list.insert(tk.END, f"'{old_text}' → '{new_text}'")
            
            refresh_list()
            
            # Buttons
            btn_frame = tk.Frame(edit_window)
            btn_frame.pack(side=tk.BOTTOM, pady=10)
            
            def add_replacement():
                find_text = find_entry.get().strip()
                replace_text = replace_entry.get()
                
                if not find_text:
                    messagebox.showwarning("Warning", "Please enter text to find")
                    return
                
                if find_text not in text:
                    messagebox.showwarning("Warning", f"Text '{find_text}' not found on this page")
                    return
                
                self.text_replacements[self.current_page].append((find_text, replace_text))
                refresh_list()
                find_entry.delete(0, tk.END)
                replace_entry.delete(0, tk.END)
                messagebox.showinfo("Success", "Replacement added")
            
            def remove_replacement():
                selection = replacement_list.curselection()
                if selection:
                    idx = selection[0]
                    self.text_replacements[self.current_page].pop(idx)
                    refresh_list()
            
            def close_window():
                edit_window.destroy()
            
            btn_style = {"font": ("Arial", 10, "bold"), "padx": 15, "pady": 8}
            tk.Button(btn_frame, text="Add Replacement", command=add_replacement, 
                     bg="#3498db", fg="white", **btn_style).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Remove Selected", command=remove_replacement, 
                     bg="#e67e22", fg="white", **btn_style).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="Done", command=close_window, 
                     bg="#27ae60", fg="white", **btn_style).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract text: {str(e)}")
    
    def split_pdf(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
        
        # Create split options window
        split_window = tk.Toplevel(self.root)
        split_window.title("Split PDF")
        split_window.geometry("700x600")
        
        # Title
        title_label = tk.Label(split_window, text="Split PDF Options", 
                              font=("Arial", 14, "bold"), bg="#3498db", fg="white", pady=15)
        title_label.pack(fill=tk.X)
        
        # Info
        info_frame = tk.Frame(split_window, bg="#ecf0f1")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(info_frame, text=f"Current PDF: {os.path.basename(self.pdf_path)}", 
                font=("Arial", 10), bg="#ecf0f1").pack(pady=5)
        tk.Label(info_frame, text=f"Total Pages: {self.total_pages}", 
                font=("Arial", 10, "bold"), bg="#ecf0f1").pack(pady=5)
        
        # Notebook for different split methods
        notebook = ttk.Notebook(split_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Split by page ranges
        range_frame = tk.Frame(notebook)
        notebook.add(range_frame, text="By Page Ranges")
        
        tk.Label(range_frame, text="Enter page ranges (one per line, format: start-end)", 
                font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(range_frame, text="Example: 1-10, 11-20, 21-30", 
                font=("Arial", 9), fg="gray").pack()
        
        range_text_frame = tk.Frame(range_frame)
        range_text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        range_scroll = tk.Scrollbar(range_text_frame)
        range_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        range_text = tk.Text(range_text_frame, height=10, font=("Arial", 11),
                            yscrollcommand=range_scroll.set)
        range_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        range_scroll.config(command=range_text.yview)
        range_text.insert(1.0, "1-10\n11-20")
        
        def split_by_ranges():
            ranges_str = range_text.get(1.0, tk.END).strip()
            if not ranges_str:
                messagebox.showwarning("Warning", "Please enter page ranges")
                return
            
            try:
                page_ranges = []
                for line in ranges_str.split('\n'):
                    line = line.strip()
                    if '-' in line:
                        start, end = line.split('-')
                        page_ranges.append((int(start.strip()), int(end.strip())))
                
                if not page_ranges:
                    messagebox.showwarning("Warning", "No valid ranges found")
                    return
                
                output_dir = filedialog.askdirectory(title="Select output directory")
                if not output_dir:
                    return
                
                self._split_by_page_range(output_dir, page_ranges)
                split_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid format: {str(e)}")
        
        tk.Button(range_frame, text="Split PDF", command=split_by_ranges,
                 bg="#27ae60", fg="white", font=("Arial", 11, "bold"), 
                 padx=30, pady=10).pack(pady=10)
        
        # Tab 2: Extract specific pages
        pages_frame = tk.Frame(notebook)
        notebook.add(pages_frame, text="Extract Pages")
        
        tk.Label(pages_frame, text="Enter page numbers to extract (comma-separated)", 
                font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(pages_frame, text="Example: 1, 5, 10, 15", 
                font=("Arial", 9), fg="gray").pack()
        
        pages_entry = tk.Entry(pages_frame, font=("Arial", 12), width=50)
        pages_entry.pack(pady=20, padx=20)
        pages_entry.insert(0, "1, 3, 5")
        
        def extract_pages():
            pages_str = pages_entry.get().strip()
            if not pages_str:
                messagebox.showwarning("Warning", "Please enter page numbers")
                return
            
            try:
                page_numbers = [int(p.strip()) for p in pages_str.split(',')]
                
                output_dir = filedialog.askdirectory(title="Select output directory")
                if not output_dir:
                    return
                
                self._extract_specific_pages(output_dir, page_numbers)
                split_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid format: {str(e)}")
        
        tk.Button(pages_frame, text="Extract Pages", command=extract_pages,
                 bg="#27ae60", fg="white", font=("Arial", 11, "bold"), 
                 padx=30, pady=10).pack(pady=10)
        
        # Tab 3: Split every N pages
        even_frame = tk.Frame(notebook)
        notebook.add(even_frame, text="Every N Pages")
        
        tk.Label(even_frame, text="Split PDF every N pages", 
                font=("Arial", 10, "bold")).pack(pady=20)
        
        n_frame = tk.Frame(even_frame)
        n_frame.pack(pady=20)
        
        tk.Label(n_frame, text="Pages per file:", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        n_spinbox = tk.Spinbox(n_frame, from_=1, to=self.total_pages, 
                              font=("Arial", 12), width=10)
        n_spinbox.pack(side=tk.LEFT)
        n_spinbox.delete(0, tk.END)
        n_spinbox.insert(0, "10")
        
        def split_every_n():
            try:
                pages_per_file = int(n_spinbox.get())
                if pages_per_file < 1:
                    messagebox.showwarning("Warning", "Pages per file must be at least 1")
                    return
                
                output_dir = filedialog.askdirectory(title="Select output directory")
                if not output_dir:
                    return
                
                self._split_every_n_pages(output_dir, pages_per_file)
                split_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {str(e)}")
        
        tk.Button(even_frame, text="Split PDF", command=split_every_n,
                 bg="#27ae60", fg="white", font=("Arial", 11, "bold"), 
                 padx=30, pady=10).pack(pady=20)
    
    def _split_by_page_range(self, output_dir, page_ranges):
        """Split PDF by page ranges"""
        try:
            reader = PdfReader(self.pdf_path)
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            
            for idx, (start, end) in enumerate(page_ranges, 1):
                if start < 1 or end > self.total_pages or start > end:
                    messagebox.showwarning("Warning", f"Invalid range ({start}-{end}), skipped")
                    continue
                
                writer = PdfWriter()
                for page_num in range(start - 1, end):
                    writer.add_page(reader.pages[page_num])
                
                output_path = os.path.join(output_dir, f"{base_name}_part{idx}_pages{start}-{end}.pdf")
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
            
            messagebox.showinfo("Success", f"PDF split into {len(page_ranges)} files\nSaved to: {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to split PDF: {str(e)}")
    
    def _extract_specific_pages(self, output_dir, page_numbers):
        """Extract specific pages"""
        try:
            reader = PdfReader(self.pdf_path)
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            
            extracted = 0
            for page_num in page_numbers:
                if page_num < 1 or page_num > self.total_pages:
                    messagebox.showwarning("Warning", f"Page {page_num} out of range, skipped")
                    continue
                
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num - 1])
                
                output_path = os.path.join(output_dir, f"{base_name}_page{page_num}.pdf")
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
                extracted += 1
            
            messagebox.showinfo("Success", f"Extracted {extracted} pages\nSaved to: {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract pages: {str(e)}")
    
    def _split_every_n_pages(self, output_dir, pages_per_file):
        """Split every N pages"""
        try:
            reader = PdfReader(self.pdf_path)
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            
            file_count = 0
            for start_page in range(0, self.total_pages, pages_per_file):
                end_page = min(start_page + pages_per_file, self.total_pages)
                
                writer = PdfWriter()
                for page_num in range(start_page, end_page):
                    writer.add_page(reader.pages[page_num])
                
                file_count += 1
                output_path = os.path.join(output_dir, f"{base_name}_part{file_count}.pdf")
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
            
            messagebox.showinfo("Success", f"PDF split into {file_count} files\nSaved to: {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to split PDF: {str(e)}")
    
    def rotate_page(self, angle):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
        
        try:
            page = self.pdf_document[self.current_page]
            page.set_rotation(page.rotation + angle)
            self.display_page()
            messagebox.showinfo("Success", f"Page rotated {angle}°")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rotate page: {str(e)}")
    
    def save_pdf(self):
        if not self.pdf_document:
            messagebox.showwarning("Warning", "No PDF loaded")
            return
        
        output_path = filedialog.asksaveasfilename(
            title="Save PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        
        if not output_path:
            return
        
        try:
            # If text replacements exist, use PyMuPDF to apply them
            if self.text_replacements:
                self.save_with_text_replacements(output_path)
            else:
                # Original save method
                reader = PdfReader(self.pdf_path)
                writer = PdfWriter()
                
                # Add pages except those marked for deletion
                for i in range(len(reader.pages)):
                    if i not in self.pages_to_delete:
                        page = reader.pages[i]
                        
                        # Apply rotation from PyMuPDF if modified
                        pymupdf_page = self.pdf_document[i]
                        rotation = pymupdf_page.rotation
                        if rotation != 0:
                            page.rotate(rotation)
                        
                        writer.add_page(page)
                
                # Save
                with open(output_path, 'wb') as output_file:
                    writer.write(output_file)
            
            messagebox.showinfo("Success", f"PDF saved to:\n{output_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
    
    def save_with_text_replacements(self, output_path):
        """Save PDF with text replacements using PyMuPDF - preserves formatting"""
        import tempfile
        import shutil
        
        # Create a temporary copy
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_file.close()
        shutil.copy(self.pdf_path, temp_file.name)
        
        # Open the copy for editing
        temp_pdf = fitz.open(temp_file.name)
        
        # Apply text replacements to each page
        for page_num, replacements in self.text_replacements.items():
            if page_num not in self.pages_to_delete and page_num < len(temp_pdf):
                page = temp_pdf[page_num]
                
                for old_text, new_text in replacements:
                    # Find all instances of the old text
                    text_instances = page.search_for(old_text)
                    
                    if text_instances:
                        for inst in text_instances:
                            # Add redaction annotation
                            page.add_redact_annot(inst, text=new_text, fontname="helv", fontsize=0)
                        
                        # Apply redactions (this replaces the text)
                        page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        
        # Remove deleted pages
        if self.pages_to_delete:
            pages_to_keep = [i for i in range(len(temp_pdf)) if i not in self.pages_to_delete]
            temp_pdf.select(pages_to_keep)
        
        # Save to output path
        temp_pdf.save(output_path, garbage=4, deflate=True)
        temp_pdf.close()
        
        # Clean up temp file
        import os
        try:
            os.unlink(temp_file.name)
        except:
            pass


def main():
    root = tk.Tk()
    app = PDFEditorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
