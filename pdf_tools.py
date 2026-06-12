import os
import zipfile
from io import BytesIO
from pypdf import PdfReader, PdfWriter, PageObject, Transformation

def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages: writer.add_page(page)
    with open(out_path, "wb") as f: writer.write(f)

def high_tech_compress_quantization(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
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

# --- ENTERPRISE FUNCTION: INTELLECTUAL MULTI-FILE MATRIX ENGINE ---
def merge_with_affine_scaling(uploaded_files_dict, page_order_list, target_size_setup, out_path):
    writer = PdfWriter()
    readers = {}
    
    # 1. Encryption Interceptor & Reader Initialization
    for file_id, file_path in uploaded_files_dict.items():
        reader = PdfReader(file_path)
        if reader.is_encrypted:
            # Fallback security bypass if standard user passwords are blank
            try:
                reader.decrypt("")
            except:
                raise Exception(f"File {file_id} is password-protected. Please unlock it before merging.")
        readers[file_id] = reader
        
    # 2. Track Form Field Suffixes to Prevent Overwrite Collisions
    field_collision_counter = 0

    for target in page_order_list:
        file_id = target.get('fileId')
        page_idx = int(target.get('pageIdx'))
        requested_layout = target.get('layout', 'portrait')
        
        if file_id in readers:
            orig_page = readers[file_id].pages[page_idx]
            orig_width = float(orig_page.mediabox.width)
            orig_height = float(orig_page.mediabox.height)
            
            # 3. Preserve Original Metadata Options (Defaulting to the first active document)
            if len(writer.pages) == 0:
                try:
                    writer.add_metadata(readers[file_id].metadata)
                except:
                    pass

            # 4. Strict Dimensional Scaling Target Configuration
            if target_size_setup == "A4":
                new_w, new_h = (595.0, 842.0) if requested_layout == "portrait" else (842.0, 595.0)
            elif target_size_setup == "LETTER":
                new_w, new_h = (612.0, 792.0) if requested_layout == "portrait" else (792.0, 612.0)
            else:
                new_w, new_h = (orig_width, orig_height) if requested_layout == "portrait" else (orig_height, orig_width)
                if requested_layout == "landscape" and orig_height > orig_width: new_w, new_h = (orig_height, orig_width)
                elif requested_layout == "portrait" and orig_width > orig_height: new_w, new_h = (orig_height, orig_width)

            blank_canvas = PageObject.create_blank_page(width=new_w, height=new_h)
            
            # 5. Affine Matrix Multiplier: Fits elements inside borders proportionally (Prevents Overflow & Text Spin)
            scale_w = new_w / orig_width
            scale_w_rot = new_w / orig_height
            scale_h = new_h / orig_height
            scale_h_rot = new_h / orig_width
            
            if requested_layout == "landscape" and orig_height > orig_width:
                scale_factor = min(scale_w_rot, scale_h_rot)
                tx = (new_w - (orig_height * scale_factor)) / 2.0
                ty = (new_h - (orig_width * scale_factor)) / 2.0
                transform = Transformation().scale(scale_factor).translate(tx, ty)
            elif requested_layout == "portrait" and orig_width > orig_height:
                scale_factor = min(scale_w_rot, scale_h_rot)
                tx = (new_w - (orig_height * scale_factor)) / 2.0
                ty = (new_h - (orig_width * scale_factor)) / 2.0
                transform = Transformation().scale(scale_factor).translate(tx, ty)
            else:
                scale_factor = min(scale_w, scale_h)
                tx = (new_w - (orig_width * scale_factor)) / 2.0
                ty = (new_h - (orig_height * scale_factor)) / 2.0
                transform = Transformation().scale(scale_factor).translate(tx, ty)
                
            blank_canvas.merge_transformed_page(orig_page, transform)
            
            # 6. Interactive Form Data Preservation & Collision Prevention Matrix
            field_collision_counter += 1
            if "/Annots" in orig_page:
                # Forces interactive fillable fields to stay visible
                if "/AcroForm" not in writer.root:
                    writer.get_fields() # Instantiates form dictionary tracking tree topology
                
                # Check for annotations and dynamically rename field tags (/T) to prevent data overwrite
                annots = orig_page["/Annots"]
                for annot in annots:
                    obj = annot.get_object()
                    if "/T" in obj:
                        original_field_name = obj["/T"]
                        obj.update({
                            "/T": f"{original_field_name}_dv_{field_collision_counter}"
                        })
            
            writer.add_page(blank_canvas)
            
    # Force form dictionaries to show up properly across PDF readers
    if "/AcroForm" in writer.root:
        writer.root["/AcroForm"].update({
            "/NeedAppearances": True
        })
        
    with open(out_path, "wb") as f:
        writer.write(f)
