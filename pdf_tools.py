import os
import zipfile
import hashlib
from io import BytesIO
from pypdf import PdfReader, PdfWriter, PageObject, Transformation
from PIL import Image

# --- 1. ENTERPRISE MERGE MATRIX ENGINE ---
def merge_with_affine_scaling(uploaded_files_dict, page_order_list, target_size_setup, out_path):
    writer = PdfWriter()
    readers = {}
    
    # Decrypt and open files safely
    for file_id, file_path in uploaded_files_dict.items():
        reader = PdfReader(file_path)
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except:
                raise Exception(f"File {file_id} is password protected. Unlock it first.")
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
            
            # Preserve metadata of first file
            if len(writer.pages) == 0:
                try: writer.add_metadata(readers[file_id].metadata)
                except: pass

            # Set exact target dimensions
            if target_size_setup == "A4":
                new_w, new_h = (595.0, 842.0) if requested_layout == "portrait" else (842.0, 595.0)
            elif target_size_setup == "LETTER":
                new_w, new_h = (612.0, 792.0) if requested_layout == "portrait" else (792.0, 612.0)
            else:
                new_w, new_h = (orig_width, orig_height) if requested_layout == "portrait" else (orig_height, orig_width)

            blank_canvas = PageObject.create_blank_page(width=new_w, height=new_h)
            
            # Proportional scaling calculations (fixes text bounds overflow)
            scale_factor = min(new_w / orig_width, new_h / orig_height)
            tx = (new_w - (orig_width * scale_factor)) / 2.0
            ty = (new_h - (orig_height * scale_factor)) / 2.0
            
            transform = Transformation().scale(scale_factor).translate(tx, ty)
            blank_canvas.merge_transformed_page(orig_page, transform)
            
            # Form field name collision protection logic
            field_collision_counter += 1
            if "/Annots" in orig_page:
                try:
                    for annot in orig_page["/Annots"]:
                        obj = annot.get_object()
                        if obj and "/T" in obj:
                            obj.update({"/T": f"{obj['/T']}_f_{field_collision_counter}"})
                except:
                    pass
            
            writer.add_page(blank_canvas)
            
    try: writer.set_need_appearances(True)
    except: pass
    
    with open(out_path, "wb") as f:
        writer.write(f)

# --- 2. MULTI-MODE SPLIT ENGINE ---
def split_pdf_advanced_core(in_path, mode, parameter_str, selected_indices, out_path_target, is_zip_request=True):
    reader = PdfReader(in_path)
    if reader.is_encrypted:
        try: reader.decrypt("")
        except: raise Exception("Password protected file.")
        
    total_pages = len(reader.pages)
    chunks_to_package = []

    if mode == "visual":
        writer = PdfWriter()
        for idx in selected_indices:
            if 0 <= idx < total_pages: writer.add_page(reader.pages[idx])
        chunks_to_package.append(("visual_split_document.pdf", writer))

    elif mode == "burst":
        for idx in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[idx])
            chunks_to_package.append((f"page_{idx + 1}.pdf", writer))

    elif mode == "chunks":
        try: chunk_size = int(parameter_str)
        except: chunk_size = 1
        chunk_size = max(1, chunk_size)
        for i in range(0, total_pages, chunk_size):
            writer = PdfWriter()
            end_range = min(i + chunk_size, total_pages)
            for idx in range(i, end_range): writer.add_page(reader.pages[idx])
            chunks_to_package.append((f"chunk_pages_{i+1}_to_{end_range}.pdf", writer))

    elif mode == "range":
        clean_str = parameter_str.replace(" ", "")
        target_indices = []
        for part in clean_str.split(","):
            if "-" in part:
                sub_parts = part.split("-")
                s_lbl, e_lbl = sub_parts[0], sub_parts[1]
                s_idx = int(s_lbl) - 1 if s_lbl else 0
                e_idx = int(e_lbl) if e_lbl else total_pages
                target_indices.extend(range(max(0, s_idx), min(e_idx, total_pages)))
            elif part:
                idx = int(part) - 1
                if 0 <= idx < total_pages: target_indices.append(idx)
        writer = PdfWriter()
        for idx in target_indices: writer.add_page(reader.pages[idx])
        chunks_to_package.append(("range_extracted_document.pdf", writer))

    if is_zip_request or len(chunks_to_package) > 1:
        with zipfile.ZipFile(out_path_target, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, writer_obj in chunks_to_package:
                buf = BytesIO()
                writer_obj.write(buf)
                buf.seek(0)
                zip_file.writestr(filename, buf.read())
        return "zip"
    else:
        with open(out_path_target, "wb") as f: chunks_to_package[0][1].write(f)
        return "pdf"

# --- 3. QUANTIZATION LOSSLESS/LOSSY COMPRESS ENGINE ---
def advanced_compress_quantization_engine(in_path, level, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    target_dpi = 150 if level == "basic" else 72
    
    for page in reader.pages:
        page.compress_content_streams() # Flates Decode text matrices
        if "/Resources" in page and "/XObject" in page["/Resources"]:
            try:
                xobjects = page["/Resources"]["/XObject"].get_object()
                for obj_id in xobjects:
                    obj = xobjects[obj_id].get_object()
                    if obj and "/Subtype" in obj and obj["/Subtype"] == "/Image":
                        img_data = obj.get_data()
                        pil_img = Image.open(BytesIO(img_data))
                        w, h = pil_img.size
                        if w > target_dpi * 8 or h > target_dpi * 8:
                            factor = (target_dpi * 8) / max(w, h)
                            pil_img = pil_img.resize((int(w * factor), int(h * factor)), Image.Resampling.LANCZOS)
                        buf = BytesIO()
                        pil_img.convert("RGB").save(buf, format="JPEG", quality=60 if level == "strong" else 80)
                        obj._data = buf.getvalue()
                        obj.update({"/Filter": "/DCTDecode"})
            except:
                pass
        writer.add_page(page)
    with open(out_path, "wb") as f: writer.write(f)
