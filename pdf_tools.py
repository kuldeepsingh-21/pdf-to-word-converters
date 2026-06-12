import os
from pypdf import PdfReader, PdfWriter

def compress_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    
    # Fix: Correctly clone pages into the new writer instance
    for page in reader.pages:
        writer.add_page(page)
        
    # Apply compression on the writer's pages
    for page in writer.pages:
        page.compress_content_streams()
        
    with open(out_path, "wb") as f:
        writer.write(f)

def repair_pdf(in_path, out_path):
    reader = PdfReader(in_path)
    writer = PdfWriter()
    # Forces reconstruction of the cross-reference tables and streams
    for page in reader.pages:
        writer.add_page(page)
    with open(out_path, "wb") as f:
        writer.write(f)