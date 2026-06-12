import os
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

def compress_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    for page in writer.pages: page.compress_content_streams()
    with open(out_path, "wb") as f: writer.write(f)

def split_advanced_pdf(in_path, page_indices, out_path):
    """
    in_path: path to uploaded target PDF
    page_indices: list of integers representing selected page orders [0, 3, 2, 5]
    out_path: path to output directory
    """
    reader = PdfReader(in_path)
    writer = PdfWriter()
    
    # Extract only the retained and arranged page objects securely
    for idx in page_indices:
        if 0 <= idx < len(reader.pages):
            page_obj = reader.pages[idx]
            writer.add_page(page_obj)
            
    with open(out_path, "wb") as f:
        writer.write(f)
def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    with open(out_path, "wb") as f: writer.write(f)

# --- ADVANCED CONTENT-CONTAINMENT MERGER ENGINE ---
def merge_with_affine_scaling(uploaded_files_dict, page_order_list, target_size_setup, out_path):
    writer = PdfWriter()
    readers = {}
    
    for file_id, file_path in uploaded_files_dict.items():
        readers[file_id] = PdfReader(file_path)
        
    for target in page_order_list:
        file_id = target.get('fileId')
        page_idx = int(target.get('pageIdx'))
        requested_layout = target.get('layout', 'portrait')
        
        if file_id in readers:
            orig_page = readers[file_id].pages[page_idx]
            orig_width = float(orig_page.mediabox.width)
            orig_height = float(orig_page.mediabox.height)
            
            # Step 1: Establish Standard Dimensions
            if target_size_setup == "A4":
                new_w, new_h = (595.0, 842.0) if requested_layout == "portrait" else (842.0, 595.0)
            elif target_size_setup == "LETTER":
                new_w, new_h = (612.0, 792.0) if requested_layout == "portrait" else (792.0, 612.0)
            else:
                new_w, new_h = (orig_width, orig_height) if requested_layout == "portrait" else (orig_height, orig_width)
                if requested_layout == "landscape" and orig_height > orig_width:
                    new_w, new_h = (orig_height, orig_width)
                elif requested_layout == "portrait" and orig_width > orig_height:
                    new_w, new_h = (orig_height, orig_width)

            blank_canvas = PageObject.create_blank_page(width=new_w, height=new_h)
            
            # Step 2: Proportional Matrix Scale Calculation (Fixes Content Overflow Bug)
            scale_w = new_w / orig_width
            scale_w_rot = new_w / orig_height
            scale_h = new_h / orig_height
            scale_h_rot = new_h / orig_width
            
            # Step 3: Map Translation Vectors and Transform Layers without Clipping
            if requested_layout == "landscape" and orig_height > orig_width:
                scale_factor = min(scale_w_rot, scale_h_rot)
                tx = (new_w - (orig_height * scale_factor)) / 2.0
                ty = (new_h - (orig_width * scale_factor)) / 2.0
                transform = Transformation().rotate(90).scale(scale_factor).translate(new_w - tx, ty)
            elif requested_layout == "portrait" and orig_width > orig_height:
                scale_factor = min(scale_w_rot, scale_h_rot)
                tx = (new_w - (orig_height * scale_factor)) / 2.0
                ty = (new_h - (orig_width * scale_factor)) / 2.0
                transform = Transformation().rotate(-90).scale(scale_factor).translate(tx, new_h - ty)
            else:
                scale_factor = min(scale_w, scale_h)
                tx = (new_w - (orig_width * scale_factor)) / 2.0
                ty = (new_h - (orig_height * scale_factor)) / 2.0
                transform = Transformation().scale(scale_factor).translate(tx, ty)
                
            blank_canvas.merge_transformed_page(orig_page, transform)
            writer.add_page(blank_canvas)
            
    with open(out_path, "wb") as f:
        writer.write(f)
