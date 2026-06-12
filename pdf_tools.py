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

def split_pdf_first_page(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    if len(reader.pages) > 0:
        writer.add_page(reader.pages[0])
    with open(out_path, "wb") as f:
        writer.write(f)

def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    with open(out_path, "wb") as f:
        writer.write(f)

def merge_advanced_pdf(uploaded_files_dict, page_order_list, out_path):
    writer = PdfWriter()
    readers = {}
    
    # Initialize a reader instance for each unique uploaded file
    for file_id, file_path in uploaded_files_dict.items():
        readers[file_id] = PdfReader(file_path)
        
    # Process the custom arranged page matrix
    for target in page_order_list:
        file_id = target.get('fileId')
        page_idx = int(target.get('pageIdx'))
        rotation_angle = int(target.get('rotation', 0)) # Extract custom layout rotation parameter
        
        if file_id in readers:
            page_obj = readers[file_id].pages[page_idx]
            
            # Apply visual orientation adjustments explicitly if changed by user
            if rotation_angle != 0:
                page_obj.rotate(rotation_angle)
                
            writer.add_page(page_obj)
            
    with open(out_path, "wb") as f:
        writer.write(f)
