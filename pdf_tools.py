import os
import zipfile
from io import BytesIO
from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from PIL import Image

def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    with open(out_path, "wb") as f: writer.write(f)

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
                file_name_inside_zip = f"extracted_page_position_{loop_idx + 1}.pdf"
                zip_file.writestr(file_name_inside_zip, memory_buffer.read())

def split_advanced_pdf(in_path, page_indices, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for idx in page_indices:
        if 0 <= idx < len(reader.pages): writer.add_page(reader.pages[idx])
    with open(out_path, "wb") as f: writer.write(f)

# --- CORRECTED SAFE MERGE ENGINE (FIXED 'root' CRASH) ---
def merge_with_affine_scaling(uploaded_files_dict, page_order_list, target_size_setup, out_path):
    writer = PdfWriter()
    readers = {}
    
    for file_id, file_path in uploaded_files_dict.items():
        reader = PdfReader(file_path)
        if reader.is_encrypted:
            try: reader.decrypt("")
            except: raise Exception(f"File {file_id} is password protected.")
        readers[file_id] = reader
        
    field_collision_counter = 0

    for target in page_order_list:
        file_id = target.get('fileId')
        page_idx = int(target.get('pageIdx'))
        requested_layout = target.get('layout', 'portrait')
        
        if file_id in readers:
            orig_page = readers[file_id].pages[page_idx]
            orig_width = float(orig_page.mediabox.width)
            orig_height = float(orig_page.mediabox.height)
            
            if len(writer.pages) == 0:
                try: writer.add_metadata(readers[file_id].metadata)
                except: pass

            if target_size_setup == "A4":
                new_w, new_h = (595.0, 842.0) if requested_layout == "portrait" else (842.0, 595.0)
            elif target_size_setup == "LETTER":
                new_w, new_h = (612.0, 792.0) if requested_layout == "portrait" else (792.0, 612.0)
            else:
                new_w, new_h = (orig_width, orig_height) if requested_layout == "portrait" else (orig_height, orig_width)

            blank_canvas = PageObject.create_blank_page(width=new_w, height=new_h)
            scale_w = new_w / orig_width ; scale_h = new_h / orig_height
            scale_factor = min(scale_w, scale_h)
            tx = (new_w - (orig_width * scale_factor)) / 2.0
            ty = (new_h - (orig_height * scale_factor)) / 2.0
            
            transform = Transformation().scale(scale_factor).translate(tx, ty)
            blank_canvas.merge_transformed_page(orig_page, transform)
            
            # Form Field Rename Sequence
            field_collision_counter += 1
            if "/Annots" in orig_page:
                for annot in orig_page["/Annots"]:
                    obj = annot.get_object()
                    if obj and "/T" in obj:
                        obj.update({"/T": f"{obj['/T']}_dv_{field_collision_counter}"})
            
            writer.add_page(blank_canvas)
            
    # FIXED: Re-enables form handling via safe, universal configuration variables
    try:
        writer.set_need_appearances(True)
    except:
        pass
        
    with open(out_path, "wb") as f:
        writer.write(f)

# --- NEW COMPREHENSIVE PDF COMPRESSION SUITE ---
def advanced_compress_quantization_engine(in_path, level, out_path):
    """
    level: "basic" (FlateDecode + 150 DPI), "strong" (FlateDecode + 72 DPI)
    """
    reader = PdfReader(in_path)
    writer = PdfWriter()
    
    # Determine the downsampling DPI cap multiplier
    target_dpi = 150 if level == "basic" else 72
    
    for page in reader.pages:
        # 1. Compress internal text, fonts, and coordinate streams using FlateDecode
        page.compress_content_streams()
        
        # 2. Intercept and compress embedded raster objects inside the resource dictionary tree
        if "/Resources" in page and "/XObject" in page["/Resources"]:
            xobjects = page["/Resources"]["/XObject"].get_object()
            for obj_id in xobjects:
                obj = xobjects[obj_id].get_object()
                if obj and "/Subtype" in obj and obj["/Subtype"] == "/Image":
                    try:
                        # Extract the raw binary image stream data safely
                        img_data = obj.get_data()
                        pil_img = Image.open(BytesIO(img_data))
                        
                        # Downscale resolution matrices if the image is high resolution
                        w, h = pil_img.size
                        if w > target_dpi * 8 or h > target_dpi * 8:
                            factor = (target_dpi * 8) / max(w, h)
                            pil_img = pil_img.resize((int(w * factor), int(h * factor)), Image.Resampling.LANCZOS)
                        
                        # Re-encode image elements back using DCTDecode (JPEG) lossy parameters
                        output_buffer = BytesIO()
                        pil_img.convert("RGB").save(output_buffer, format="JPEG", quality=65 if level == "strong" else 80)
                        
                        # Update object dictionaries
                        obj._data = output_buffer.getvalue()
                        if "/Filter" in obj:
                            obj.update({"/Filter": "/DCTDecode"})
                    except:
                        pass # Skips individual images that use unmapped encoding types
                        
        writer.add_page(page)
        
    with open(out_path, "wb") as f:
        writer.write(f)
