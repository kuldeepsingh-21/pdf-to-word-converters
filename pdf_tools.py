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

# --- ADVANCED TRUE PAGE-SETUP ENGINE REBUILD ---
def merge_with_page_setup(uploaded_files_dict, page_order_list, out_path):
    writer = PdfWriter()
    readers = {}
    
    for file_id, file_path in uploaded_files_dict.items():
        readers[file_id] = PdfReader(file_path)
        
    for target in page_order_list:
        file_id = target.get('fileId')
        page_idx = int(target.get('pageIdx'))
        requested_layout = target.get('layout', 'portrait') # Read layout parameter "portrait" or "landscape"
        
        if file_id in readers:
            page_obj = readers[file_id].pages[page_idx]
            
            # Extract actual page view media box dimensions
            media_box = page_obj.mediabox
            current_width = float(media_box.width)
            current_height = float(media_box.height)
            
            # TRUE PAGE SETUP DIMENSION LOGIC:
            # If landscape is requested but page height is taller than width, re-dimension the actual file page parameters
            if requested_layout == "landscape" and current_height > current_width:
                page_obj.mediabox.left = media_box.bottom
                page_obj.mediabox.bottom = media_box.left
                page_obj.mediabox.right = media_box.top
                page_obj.mediabox.top = media_box.right
                page_obj.rotate(90) # Rotate contents to adapt clean mapping alignments
                
            # If portrait is requested but page width is wider than height, convert it back
            elif requested_layout == "portrait" and current_width > current_height:
                page_obj.mediabox.left = media_box.bottom
                page_obj.mediabox.bottom = media_box.left
                page_obj.mediabox.right = media_box.top
                page_obj.mediabox.top = media_box.right
                page_obj.rotate(-90)
                
            writer.add_page(page_obj)
            
    with open(out_path, "wb") as f:
        writer.write(f)
