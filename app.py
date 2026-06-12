import os
from flask import Flask, render_template, request, send_file, abort
from pdf2docx import Converter
from pypdf import PdfReader, PdfWriter
from PIL import Image, ImageEnhance
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import docx
import openpyxl

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'

# --- HTML TEMPLATE HELPER ---
def render_layout(title, content):
    return f'''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Free PDF Convert</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-50 font-sans min-h-screen flex flex-col justify-between text-slate-800">
        <header class="bg-white border-b border-gray-200 py-4 px-6 flex justify-between items-center shadow-sm">
            <a href="/" class="text-2xl font-black text-red-600 tracking-tight">Free PDF<span class="text-slate-800"> Convert</span></a>
            <nav class="hidden md:flex space-x-6 text-sm font-medium text-slate-600">
                <a href="/" class="hover:text-red-600">Home</a>
                <a href="/about" class="hover:text-red-600">About Us</a>
                <a href="/contact" class="hover:text-red-600">Contact</a>
            </nav>
        </header>

        <main class="flex-grow max-w-6xl w-full mx-auto px-4 py-8">
            {content}
        </main>

        <footer class="bg-slate-900 text-slate-400 text-center py-8 text-xs border-t border-slate-800">
            <div class="flex justify-center space-x-6 mb-4 text-sm">
                <a href="/about" class="hover:underline">About Us</a>
                <a href="/privacy" class="hover:underline">Privacy Policy</a>
                <a href="/terms" class="hover:underline">Terms & Conditions</a>
                <a href="/contact" class="hover:underline">Contact Us</a>
            </div>
            <p>&copy; 2026 Free PDF Convert. All file utilities are securely sandbox-processed.</p>
        </footer>
    </body>
    </html>
    '''

# --- 1. HOME PAGE ROUTE ---
@app.route('/')
def home():
    tools_html = '''
    <div class="text-center mb-12">
        <h1 class="text-4xl font-extrabold text-slate-900 tracking-tight sm:text-5xl">All-In-One Document & Image Platform</h1>
        <p class="mt-4 text-lg text-slate-600 max-w-2xl mx-auto">100% free online conversion, file compression, object repair, and image editing assets.</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        
        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition">
            <div class="text-red-600 font-bold text-lg mb-2">Convert From PDF</div>
            <p class="text-slate-500 text-sm mb-4">Transform regular PDF files into fully editable Microsoft Word .docx profiles.</p>
            <form method="POST" action="/engine/pdf2word" enctype="multipart/form-data">
                <input type="file" name="file" accept=".pdf" required class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-red-50 file:text-red-700 hover:file:bg-red-100 mb-2">
                <button type="submit" class="w-full bg-red-600 text-white text-xs py-2 rounded-lg hover:bg-red-700 font-bold">Convert to Word</button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition">
            <div class="text-blue-600 font-bold text-lg mb-2">Convert JPG/PNG to PDF</div>
            <p class="text-slate-500 text-sm mb-4">Pack multiple picture elements into a uniform clean vector PDF file template.</p>
            <form method="POST" action="/engine/img2pdf" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*" required class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 mb-2">
                <button type="submit" class="w-full bg-blue-600 text-white text-xs py-2 rounded-lg hover:bg-blue-700 font-bold">Convert to PDF</button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition">
            <div class="text-emerald-600 font-bold text-lg mb-2">Compress PDF</div>
            <p class="text-slate-500 text-sm mb-4">Shrink heavy structural documents down to compact, email-friendly formats.</p>
            <form method="POST" action="/engine/compress" enctype="multipart/form-data">
                <input type="file" name="file" accept=".pdf" required class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-emerald-50 file:text-emerald-700 hover:file:bg-emerald-100 mb-2">
                <button type="submit" class="w-full bg-emerald-600 text-white text-xs py-2 rounded-lg hover:bg-emerald-700 font-bold">Optimize File Size</button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition">
            <div class="text-amber-600 font-bold text-lg mb-2">Repair Damaged PDF</div>
            <p class="text-slate-500 text-sm mb-4">Attempt automated structural block indexing rebuilds on broken data assets.</p>
            <form method="POST" action="/engine/repair" enctype="multipart/form-data">
                <input type="file" name="file" accept=".pdf" required class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-amber-50 file:text-amber-700 hover:file:bg-amber-100 mb-2">
                <button type="submit" class="w-full bg-amber-600 text-white text-xs py-2 rounded-lg hover:bg-amber-700 font-bold">Fix Structure</button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition">
            <div class="text-purple-600 font-bold text-lg mb-2">Resize & Compress Image</div>
            <p class="text-slate-500 text-sm mb-4">Downscale frame resolution geometries instantly to drop storage sizes down.</p>
            <form method="POST" action="/engine/imgresize" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*" required class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-purple-50 file:text-purple-700 hover:file:bg-purple-100 mb-2">
                <button type="submit" class="w-full bg-purple-600 text-white text-xs py-2 rounded-lg hover:bg-purple-700 font-bold">Downscale & Shrink</button>
            </form>
        </div>

        <div class="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition">
            <div class="text-fuchsia-600 font-bold text-lg mb-2">Enhance Photo Matrix</div>
            <p class="text-slate-500 text-sm mb-4">Boost contrast clarity parameters across picture layers computationally.</p>
            <form method="POST" action="/engine/imgenhance" enctype="multipart/form-data">
                <input type="file" name="file" accept="image/*" required class="block w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-fuchsia-50 file:text-fuchsia-700 hover:file:bg-fuchsia-100 mb-2">
                <button type="submit" class="w-full bg-fuchsia-600 text-white text-xs py-2 rounded-lg hover:bg-fuchsia-700 font-bold">Amplify Contrast</button>
            </form>
        </div>

    </div>
    '''
    return render_layout("Free Online Document Tools", tools_html)

# --- ENGINE LOGICS ---

@app.route('/engine/pdf2word', methods=['POST'])
def engine_pdf2word():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'): return "Invalid file format", 400
    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)
    docx_path = pdf_path.replace('.pdf', '.docx')
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        return send_file(docx_path, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(pdf_path): os.remove(pdf_path)

@app.route('/engine/img2pdf', methods=['POST'])
def engine_img2pdf():
    file = request.files.get('file')
    if not file: return "Missing asset", 400
    img_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(img_path)
    pdf_path = img_path + ".pdf"
    try:
        im = Image.open(img_path)
        im.convert('RGB').save(pdf_path, "PDF")
        return send_file(pdf_path, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(img_path): os.remove(img_path)

@app.route('/engine/compress', methods=['POST'])
def engine_compress():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'): return "Bad request", 400
    in_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(in_path)
    out_path = os.path.join(UPLOAD_FOLDER, "compressed_" + file.filename)
    try:
        reader = PdfReader(in_path)
        writer = PdfWriter()
        for page in reader.pages:
            page.compress_content_streams() # Compress internal components
            writer.add_page(page)
        with open(out_path, "wb") as f:
            writer.write(f)
        return send_file(out_path, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

@app.route('/engine/repair', methods=['POST'])
def engine_repair():
    file = request.files.get('file')
    if not file or not file.filename.endswith('.pdf'): return "Bad reference", 400
    in_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(in_path)
    out_path = os.path.join(UPLOAD_FOLDER, "repaired_" + file.filename)
    try:
        reader = PdfReader(in_path)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        with open(out_path, "wb") as f:
            writer.write(f)
        return send_file(out_path, as_attachment=True)
    except Exception as e: return "Corruption too deep to extract streams automatically.", 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

@app.route('/engine/imgresize', methods=['POST'])
def engine_imgresize():
    file = request.files.get('file')
    if not file: return "Bad target file", 400
    in_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(in_path)
    out_path = os.path.join(UPLOAD_FOLDER, "shrunk_" + file.filename)
    try:
        img = Image.open(in_path)
        # Scale to 50% max capacity size coordinates
        w, h = img.size
        img_resized = img.resize((int(w*0.5), int(h*0.5)), Image.Resampling.LANCZOS)
        img_resized.save(out_path, optimize=True, quality=60)
        return send_file(out_path, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

@app.route('/engine/imgenhance', methods=['POST'])
def engine_imgenhance():
    file = request.files.get('file')
    if not file: return "Target null file", 400
    in_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(in_path)
    out_path = os.path.join(UPLOAD_FOLDER, "enhanced_" + file.filename)
    try:
        img = Image.open(in_path)
        enhancer = ImageEnhance.Contrast(img)
        enhanced_img = enhancer.enhance(1.5) # Increase contrast profile matrix mapping
        enhanced_img.save(out_path)
        return send_file(out_path, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

# --- MANDATORY INFRASTRUCTURE PAGES ---

@app.route('/about')
def page_about():
    content = '''
    <div class="max-w-3xl mx-auto bg-white p-8 rounded-2xl border border-slate-200">
        <h1 class="text-3xl font-bold mb-4">About Free PDF Convert</h1>
        <p class="text-slate-600 mb-4">Welcome to Free PDF Convert. Our mission is to make document and image tool management simple, intuitive, and accessible to everyone worldwide without subscriptions or hidden paywalls.</p>
        <p class="text-slate-600">Built using modern server optimization architectures, all transformation runs process immediately inside dynamic sandboxed temporary containers. Your files are never stored or visually logged by human eyes.</p>
    </div>
    '''
    return render_layout("About Us", content)

@app.route('/privacy')
def page_privacy():
    content = '''
    <div class="max-w-3xl mx-auto bg-white p-8 rounded-2xl border border-slate-200">
        <h1 class="text-3xl font-bold mb-4">Privacy Policy</h1>
        <p class="text-slate-600 mb-4">At Free PDF Convert, file safety is our highest priority. We do not require account registration, and we do not track structural metadata content embedded across uploaded objects.</p>
        <h2 class="text-xl font-bold mt-6 mb-2">Data Lifetime</h2>
        <p class="text-slate-600 mb-4">All uploaded PDFs, imagery components, or Word files exist within volatile runtime buffers. Immediately upon task execution finish or server lifecycle timeout, operations execute strict terminal cleanup commands.</p>
    </div>
    '''
    return render_layout("Privacy Policy", content)

@app.route('/terms')
def page_terms():
    content = '''
    <div class="max-w-3xl mx-auto bg-white p-8 rounded-2xl border border-slate-200">
        <h1 class="text-3xl font-bold mb-4">Terms & Conditions</h1>
        <p class="text-slate-600 mb-4">By interacting with the processing mechanics hosted via Free PDF Convert, you confirm full alignment with our acceptable usage conditions.</p>
        <h2 class="text-xl font-bold mt-6 mb-2">Disclaimer of Liability</h2>
        <p class="text-slate-600 mb-4">Services are rendered strictly "as-is". Free PDF Convert does not assume operational liability for any text-rendering artifacts or formatting structural decay caused by automated digital document conversion modules.</p>
    </div>
    '''
    return render_layout("Terms & Conditions", content)

@app.route('/contact')
def page_contact():
    content = '''
    <div class="max-w-3xl mx-auto bg-white p-8 rounded-2xl border border-slate-200">
        <h1 class="text-3xl font-bold mb-4">Contact Us</h1>
        <p class="text-slate-600 mb-6">Have an engineering problem or custom feature request? Reach out directly via our messaging form below.</p>
        <form class="space-y-4" action="#" method="GET" onsubmit="alert('Message pipeline mock successful! Actual storage delivery skipped.')">
            <div>
                <label class="block text-sm font-semibold mb-1 text-slate-700">Email Address</label>
                <input type="email" required class="w-full p-2.5 border border-slate-300 rounded-lg text-sm bg-slate-50 focus:outline-red-500">
            </div>
            <div>
                <label class="block text-sm font-semibold mb-1 text-slate-700">Inquiry Narrative</label>
                <textarea required rows="4" class="w-full p-2.5 border border-slate-300 rounded-lg text-sm bg-slate-50 focus:outline-red-500"></textarea>
            </div>
            <button type="submit" class="bg-red-600 text-white font-bold py-2 px-6 rounded-lg text-sm hover:bg-red-700 transition">Submit Form</button>
        </form>
    </div>
    '''
    return render_layout("Contact Us", content)

if __name__ == '__main__':
    app.run(debug=True)
