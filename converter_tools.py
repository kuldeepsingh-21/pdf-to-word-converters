import os
import hashlib
from io import BytesIO
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def pdf_to_word(pdf_path, docx_path):
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()

def img_to_pdf_adjusted(img_path, pdf_path, orientation="portrait", margins="none"):
    img = Image.open(img_path)
    if orientation == "landscape" and img.height > img.width: img = img.rotate(90, expand=True)
    elif orientation == "portrait" and img.width > img.height: img = img.rotate(-90, expand=True)
    img_converted = img.convert("RGB")
    img_converted.save(pdf_path, "PDF", resolution=100.0, quality=90)

def html_web_capture_to_pdf(html_text_content, out_pdf_path, convert_to_pdf_a=False):
    c = canvas.Canvas(out_pdf_path, pagesize=letter)
    width, height = letter
    y_position = height - 50
    content_dedup_db = set()
    link_counter = 0
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, "Web Capture Converted Document")
    y_position -= 35
    
    for line in html_text_content.split('\n'):
        if not line.strip(): continue
        line_fingerprint = hashlib.md5(line.encode('utf-8')).hexdigest()
        if line_fingerprint in content_dedup_db: continue
        content_dedup_db.add(line_fingerprint)
        
        if "href" in line or "http" in line:
            link_counter += 1
            unique_name = f"anchor_node_{line_fingerprint[:6]}_{link_counter}"
            c.setFillColorRGB(0.85, 0.2, 0.1)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y_position, f"[{unique_name.upper()}]: {line.strip()[:80]}")
        else:
            c.setFillColorRGB(0.2, 0.2, 0.2)
            c.setFont("Helvetica", 9)
            c.drawString(50, y_position, line.strip()[:100])
            
        y_position -= 18
        if y_position < 50:
            c.showPage()
            y_position = height - 50
    c.save()

    if convert_to_pdf_a:
        r = PdfReader(out_pdf_path) ; w = PdfWriter()
        for p in r.pages: w.add_page(p)
        w.add_metadata({"/GTS_PDFA14": "Yes", "/Title": "Preserved PDF/A Archival"})
        with open(out_pdf_path, "wb") as f: w.write(f)

def extract_images_from_pdf(pdf_path, output_folder):
    reader = PdfReader(pdf_path)
    generated_files = []
    for idx, page in enumerate(reader.pages):
        if "/Resources" in page and "/XObject" in page["/Resources"]:
            try:
                xobjects = page["/Resources"]["/XObject"].get_object()
                for obj_id in xobjects:
                    obj = xobjects[obj_id].get_object()
                    if obj and obj["/Subtype"] == "/Image":
                        raw = obj.get_data()
                        pil_img = Image.open(BytesIO(raw))
                        path = os.path.join(output_folder, f"extracted_p{idx+1}_{obj_id[1:]}.jpg")
                        pil_img.convert("RGB").save(path, "JPEG")
                        generated_files.append(path)
            except: pass
    return generated_files
