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

def merge_with_affine_scaling(uploaded_files_dict, page_order_list, target_size_setup, out_path):
    writer = PdfWriter()
    readers = {}
    for file_id, file_path in uploaded_files_dict.items():
        reader = PdfReader(file_path)
        if reader.is_encrypted:
            try: reader.decrypt("")
            except: raise Exception(f"File {file_id} is locked. Unlock it before merging.")
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
            if target_size_setup == "A4":
                new_w, new_h = (595.0, 842.0) if requested_layout == "portrait" else (842.0, 595.0)
            elif target_size_setup == "LETTER":
                new_w, new_h = (612.0, 792.0) if requested_layout == "portrait" else (792.0, 612.0)
            else:
                new_w, new_h = (orig_width, orig_height) if requested_layout == "portrait" else (orig_height, orig_width)
                if requested_layout == "landscape" and orig_height > orig_width: new_w, new_h = (orig_height, orig_width)
                elif requested_layout == "portrait" and orig_width > orig_height: new_w, new_h = (orig_height, orig_width)
            blank_canvas = PageObject.create_blank_page(width=new_w, height=new_h)
            scale_w = new_w / orig_width ; scale_h = new_h / orig_height
            scale_factor = min(scale_w, scale_h)
            tx = (new_w - (orig_width * scale_factor)) / 2.0
            ty = (new_h - (orig_height * scale_factor)) / 2.0
            transform = Transformation().scale(scale_factor).translate(tx, ty)
            blank_canvas.merge_transformed_page(orig_page, transform)
            field_collision_counter += 1
            if "/Annots" in orig_page:
                if "/AcroForm" not in writer.root: writer.get_fields()
                for annot in orig_page["/Annots"]:
                    obj = annot.get_object()
                    if "/T" in obj: obj.update({"/T": f"{obj['/T']}_dv_{field_collision_counter}"})
            writer.add_page(blank_canvas)
    if "/AcroForm" in writer.root: writer.root["/AcroForm"].update({"/NeedAppearances": True})
    with open(out_path, "wb") as f: writer.write(f)

# --- ADVANCED SPLIT SYSTEM ENGINE (HANDLES BOTH ZIP AND PDF PIECES) ---
def split_pdf_advanced_core(in_path, mode, parameter_str, selected_indices, out_path_target, is_zip_request=True):
    reader = PdfReader(in_path)
    if reader.is_encrypted:
        try: reader.decrypt("")
        except: raise Exception("This file is encrypted with a password. Please unlock it before processing.")
        
    total_pages = len(reader.pages)
    chunks_to_package = [] # List of tuples: (filename, page_object_list)

    # Mode 1: Visual Picker Elements
    if mode == "visual":
        if not selected_indices: raise Exception("No pages selected in the grid layout workspace.")
        writer = PdfWriter()
        for idx in selected_indices:
            if 0 <= idx < total_pages: writer.add_page(reader.pages[idx])
        chunks_to_package.append(("visual_extracted_document.pdf", writer))

    # Mode 2: Burst into single pages
    elif mode == "burst":
        for idx in range(total_pages):
            writer = PdfWriter()
            writer.add_page(reader.pages[idx])
            chunks_to_package.append((f"burst_page_{idx + 1}.pdf", writer))

    # Mode 3: Split by Chunks
    elif mode == "chunks":
        try: chunk_size = int(parameter_str)
        except: chunk_size = 1
        if chunk_size < 1: chunk_size = 1
        
        for i in range(0, total_pages, chunk_size):
            writer = PdfWriter()
            end_range = min(i + chunk_size, total_pages)
            for idx in range(i, end_range):
                writer.add_page(reader.pages[idx])
            chunks_to_package.append((f"split_chunk_pages_{i+1}_to_{end_range}.pdf", writer))

    # Mode 4: Range Input Fields (Handles open-ended sequences like '12-')
    elif mode == "range":
        clean_str = parameter_str.replace(" ", "")
        target_indices = []
        for part in clean_str.split(","):
            if "-" in part:
                sub_parts = part.split("-")
                start_lbl = sub_parts[0]
                end_lbl = sub_parts[1]
                
                start_idx = int(start_lbl) - 1 if start_lbl else 0
                end_idx = int(end_lbl) if end_lbl else total_pages
                
                start_idx = max(0, min(start_idx, total_pages))
                end_idx = max(0, min(end_idx, total_pages))
                target_indices.extend(range(start_idx, end_idx))
            else:
                if part:
                    idx = int(part) - 1
                    if 0 <= idx < total_pages: target_indices.append(idx)
                    
        if not target_indices: raise Exception("Invalid range fields generated.")
        writer = PdfWriter()
        for idx in target_indices: writer.add_page(reader.pages[idx])
        chunks_to_package.append(("range_extracted_document.pdf", writer))

    # Package Output into the Target Directory (ZIP vs Single PDF)
    if is_zip_request or len(chunks_to_package) > 1:
        with zipfile.ZipFile(out_path_target, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for filename, writer_obj in chunks_to_package:
                buf = BytesIO()
                writer_obj.write(buf)
                buf.seek(0)
                zip_file.writestr(filename, buf.read())
        return "zip"
    else:
        with open(out_path_target, "wb") as f:
            chunks_to_package[0][1].write(f)
        return "pdf"
