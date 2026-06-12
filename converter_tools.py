from pdf2docx import Converter
from PIL import Image

def pdf_to_word(pdf_path, docx_path):
    cv = Converter(pdf_path)
    cv.convert(docx_path, start=0, end=None)
    cv.close()

def img_to_pdf(img_path, pdf_path):
    im = Image.open(img_path)
    im.convert('RGB').save(pdf_path, "PDF")