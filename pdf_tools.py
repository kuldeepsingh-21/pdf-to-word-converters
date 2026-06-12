import os
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

def compress_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    for page in writer.pages: page.compress_content_streams()
    with open(out_path, "wb") as f: writer.write(f)

def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    with open(out_path, "wb") as f: writer.write(f)

# --- ADVANCED AFFINE SCALING & OUT-OF-BOUNDS CONTENT RESCALE LOGIC ---
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
            
            # Step 1: Establish Strict Standard Target Canvas Boundary Geometries (A4 vs Letter vs Original)
            if target_size_setup == "A4":
                new_w, new_h = (595.0, 842.0) if requested_layout == "portrait" else (842.0, 595.0)
            elif target_size_setup == "LETTER":
                new_w, new_h = (612.0, 792.0) if requested_layout == "portrait" else (792.0, 612.0)
            else:
                # Default "original" dimension tracking
                new_w, new_h = (orig_width, orig_height) if requested_layout == "portrait" else (orig_height, orig_width)
                if requested_layout == "landscape" and orig_height > orig_width:
                    new_w, new_h = (orig_height, orig_width)
                elif requested_layout == "portrait" and orig_width > orig_height:
                    new_w, new_h = (orig_height, orig_width)

            # Create an empty, normalized target container canvas sheet matching the exact setup dimensions
            blank_canvas = PageObject.create_blank_page(width=new_w, height=new_h)
            
            # Step 2: Compute Aspect Ratios to enforce strict containment guidelines (Prevents Out-Of-Bounds Clipping)
            scale_w = new_w / orig_width
            scale_h = new_h / orig_height
            scale_factor = min(scale_w, scale_h) # Affine matrix scaling operator
            
            # Step 3: Compute exact offset shifts to center text content layers perfectly
            fit_width = orig_width * scale_factor
            fit_height = orig_height * scale_factor
            tx = (new_w - fit_width) / 2.0
            ty = (new_h - fit_height) / 2.0
            
            # Step 4: Construct transformation matrix arrays and merge the source layers safely
            transform = Transformation().scale(scale_factor).translate(tx, ty)
            
            # High-Tech Alignment Logic: If orientation setup changes, spin the core content matrix inside the canvas boundaries
            if requested_layout == "landscape" and orig_height > orig_width:
                transform = Transformation().rotate(90).scale(scale_factor).translate(new_w - tx, ty)
            elif requested_layout == "portrait" and orig_width > orig_height:
                transform = Transformation().rotate(-90).scale(scale_factor).translate(tx, new_h - ty)
                
            blank_canvas.merge_transformed_page(orig_page, transform)
            writer.add_page(blank_canvas)
            
    with open(out_path, "wb") as f:
        writer.write(f)
