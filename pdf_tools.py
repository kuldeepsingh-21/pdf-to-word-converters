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

# --- ADVANCED HIGH-TECH ORIENTATION & TEXT ROTATION REBUILD ---
def merge_with_page_setup(uploaded_files_dict, page_order_list, out_path):
    writer = PdfWriter()
    readers = {}
    
    for file_id, file_path in uploaded_files_dict.items():
        readers[file_id] = PdfReader(file_path)
        
    for target in page_order_list:
        file_id = target.get('fileId')
        page_idx = int(target.get('pageIdx'))
        requested_layout = target.get('layout', 'portrait')
        
        if file_id in readers:
            page_obj = readers[file_id].pages[page_idx]
            
            media_box = page_obj.mediabox
            current_width = float(media_box.width)
            current_height = float(media_box.height)
            
            # Condition A: Original file page is portrait, but user forces it to Landscape Page Setup
            if requested_layout == "landscape" and current_height >= current_width:
                # Force swap physical width and height vectors of the media margins canvas
                page_obj.mediabox.left = media_box.bottom
                page_obj.mediabox.bottom = media_box.left
                page_obj.mediabox.right = media_box.top
                page_obj.mediabox.top = media_box.right
                
                # High-Tech Matrix transformation: physically turn text characters 90 degrees to fit layout flow
                page_obj.rotate(90)
                
            # Condition B: Original file page is landscape, but user forces it to Portrait Page Setup
            elif requested_layout == "portrait" and current_width > current_height:
                page_obj.mediabox.left = media_box.bottom
                page_obj.mediabox.bottom = media_box.left
                page_obj.mediabox.right = media_box.top
                page_obj.mediabox.top = media_box.right
                
                # Physically turn text characters back -90 degrees into portrait alignment flow
                page_obj.rotate(-90)
                
            # Condition C: Keeps original file layout setup unchanged (if it matches perfectly)
            else:
                pass
                
            writer.add_page(page_obj)
            
    with open(out_path, "wb") as f:
        writer.write(f)
