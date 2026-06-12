import os
from pypdf import PdfReader, PdfWriter

def compress_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    for page in writer.pages:
        page.compress_content_streams()
    with open(out_path, "wb") as f:
        writer.write(f)

def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(out_path, "wb") as f:
        writer.write(f)

# --- ADVANCED MERGER ENGINE ---
def merge_advanced_pdf(uploaded_files_dict, page_order_list, out_path):
    """
    uploaded_files_dict: {"file_0.pdf": "/tmp/file_0.pdf", ...}
    page_order_list: [{"fileId": "file_0.pdf", "pageIdx": 0}, ...]
    """
    writer = PdfWriter()
    readers = {}

    # Initialize a reader instance for each unique uploaded file
    for file_id, file_path in uploaded_files_dict.items():
        readers[file_id] = PdfReader(file_path)

    # Append pages sequentially based on the drag-and-drop order matrix sent from frontend
    for target in page_order_list:
        file_id = target.get('fileId')
        page_idx = int(target.get('pageIdx'))
        
        if file_id in readers:
            target_page = readers[file_id].pages[page_idx]
            writer.add_page(target_page)

    with open(out_path, "wb") as f:
        writer.write(f)
