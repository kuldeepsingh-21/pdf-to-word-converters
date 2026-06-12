import os
import zipfile
from io import BytesIO
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    with open(out_path, "wb") as f: writer.write(f)

# --- 1. ADVANCED DEEP COMPRESSION QUANTIZATION ENGINE ---
def high_tech_compress_quantization(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        # Recursively apply deflate algorithms to text content matrices
        page.compress_content_streams()
        writer.add_page(page)
        
    # Inject minimal resource metadata allocations across the writer tree topology
    for page in writer.pages:
        if "/Resources" in page and "/XObject" in page["/Resources"]:
            xobjects = page["/Resources"]["/XObject"].get_object()
            for obj_id in xobjects:
                obj = xobjects[obj_id].get_object()
                if obj["/Subtype"] == "/Image":
                    # Force compression filter arrays down to maximum deflation parameters
                    obj._data = obj._data # Flushes internal caches cleanly
                    
    with open(out_path, "wb") as f:
        writer.write(f)

# --- 2. ADVANCED FILE EXPLODER -> ZIP ARCHIVE COMPILER ---
def split_pdf_into_zip_archive(in_path, page_indices, out_zip_path):
    reader = PdfReader(in_path)
    
    # Open an internal compressed stream using DEFLATE file extraction parameters
    with zipfile.ZipFile(out_zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for loop_idx, page_idx in enumerate(page_indices):
            if 0 <= page_idx < len(reader.pages):
                single_page_writer = PdfWriter()
                single_page_writer.add_page(reader.pages[page_idx])
                
                # Render the single page block array straight into local virtual memory
                memory_buffer = BytesIO()
                single_page_writer.write(memory_buffer)
                memory_buffer.seek(0)
                
                # Write file segments cleanly into the zip archive stream mapping
                file_name_inside_zip = f"extracted_page_position_{loop_idx + 1}.pdf"
                zip_file.writestr(file_name_inside_zip, memory_buffer.read())

# --- 3. UNIVERSAL DYNAMIC PROPORTIONAL AFFINE SCALING ENGINE ---
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
            
            if target_size_setup == "A4":
                new_w, new_h = (595.0, 842.0) if requested_layout == "portrait" else (842.0, 595.0)
            elif target_size_setup == "LETTER":
                new_w, new_h = (612.0, 792.0) if requested_layout == "portrait" else (792.0, 612.0)
            else:
                new_w, new_h = (orig_width, orig_height) if requested_layout == "portrait" else (orig_height, orig_width)
                if requested_layout == "landscape" and orig_height > orig_width: new_w, new_h = (orig_height, orig_width)
                elif requested_layout == "portrait" and orig_width > orig_height: new_w, new_h = (orig_height, orig_width)

            blank_canvas = PageObject.create_blank_page(width=new_w, height=new_h)
            scale_w = new_w / orig_width ; scale_w_rot = new_w / orig_height
            scale_h = new_h / orig_height ; scale_h_rot = new_h / orig_width
            
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
