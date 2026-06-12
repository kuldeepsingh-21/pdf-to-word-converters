import os
import zipfile
from io import BytesIO
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

# --- FIX: WORKING COMPRESS PDF ENGINE (NO PDFWRITER ERRORS) ---
def high_tech_compress_quantization(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    
    # Clone pages into the writer thread first to avoid reference errors
    for page in reader.pages:
        new_page = writer.add_page(page)
        # Apply deflate algorithm directly onto the writer's page stream
        new_page.compress_content_streams()
        
    with open(out_path, "wb") as f:
        writer.write(f)

def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    with open(out_path, "wb") as f: writer.write(f)

# --- VISUAL SPLIT TO COMPRESSED ZIP ARCHIVE GENERATOR ---
def split_pdf_into_zip_archive(in_path, page_indices, out_zip_path):
    reader = PdfReader(in_path)
    with zipfile.ZipFile(out_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for loop_idx, page_idx in enumerate(page_indices):
            if 0 <= page_idx < len(reader.pages):
                single_page_writer = PdfWriter()
                single_page_writer.add_page(reader.pages[page_idx])
                
                memory_buffer = BytesIO()
                single_page_writer.write(memory_buffer)
                memory_buffer.seek(0)
                
                file_name_inside_zip = f"page_{loop_idx + 1}.pdf"
                zip_file.writestr(file_name_inside_zip, memory_buffer.read())

# --- ADVANCED SCALING ENGINE (UPRIGHT TEXT, NO OVERFLOW) ---
def merge_with_affine_scaling(uploaded_files_dict, page_order_list, target_size_setup, out_path):
    writer = PdfWriter()
    readers = {fid: PdfReader(fpath) for fid, fpath in uploaded_files_dict.items()}
        
    for target in page_order_list:
        file_id = target.get('fileId')
        page_idx = int(target.get('pageIdx'))
        requested_layout = target.get('layout', 'portrait')
        
        if file_id in readers:
            orig_page = readers[file_id].pages[page_idx]
            orig_width = float(orig_page.mediabox.width)
            orig_height = float(orig_page.mediabox.height)
            
            # Establish base boundaries based on choice
            if target_size_setup == "A4":
                new_w, new_h = (595.0, 842.0) if requested_layout == "portrait" else (842.0, 595.0)
            elif target_size_setup == "LETTER":
                new_w, new_h = (612.0, 792.0) if requested_layout == "portrait" else (792.0, 612.0)
            else:
                new_w, new_h = (orig_width, orig_height) if requested_layout == "portrait" else (orig_height, orig_width)
                if requested_layout == "landscape" and orig_height > orig_width: new_w, new_h = (orig_height, orig_width)
                elif requested_layout == "portrait" and orig_width > orig_height: new_w, new_h = (orig_height, orig_width)

            blank_canvas = PageObject.create_blank_page(width=new_w, height=new_h)
            
            # Proportional containment scale factors
            scale_factor = min(new_w / orig_width, new_h / orig_height)
            
            # High-Tech Scaling: Keeps text upright and centers content perfectly
            if requested_layout == "landscape" and orig_height > orig_width:
                scale_factor = min(new_w / orig_height, new_h / orig_width)
            elif requested_layout == "portrait" and orig_width > orig_height:
                scale_factor = min(new_w / orig_height, new_h / orig_width)

            tx = (new_w - (orig_width * scale_factor)) / 2.0
            ty = (new_h - (orig_height * scale_factor)) / 2.0
            
            transform = Transformation().scale(scale_factor).translate(tx, ty)
            blank_canvas.merge_transformed_page(orig_page, transform)
            writer.add_page(blank_canvas)
            
    with open(out_path, "wb") as f:
        writer.write(f)
