import os
import json
import zipfile
from flask import Flask, request, send_file
import pdf_tools
import image_tools
import converter_tools

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'

def render_layout(title, content):
    return f'''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Free PDF Convert</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.min.js"></script>
    </head>
    <body class="bg-[#f2f3f8] text-[#333333] font-sans min-h-screen flex flex-col justify-between">
        
        <header class="bg-white border-b border-gray-200 py-3.5 px-6 flex justify-between items-center shadow-sm sticky top-0 z-50">
            <div class="flex items-center space-x-8">
                <a href="/" class="text-2xl font-black text-[#e5322b] tracking-tight flex items-center">
                    Free PDF<span class="text-[#333333] font-bold">Convert</span>
                </a>
                <nav class="hidden lg:flex space-x-6 text-sm font-bold text-gray-700 uppercase tracking-wide">
                    <a href="/?tool=merge" class="hover:text-[#e5322b] transition">Merge PDF</a>
                    <a href="/?tool=split" class="hover:text-[#e5322b] transition">Split PDF</a>
                    <a href="/?tool=compress" class="hover:text-[#e5322b] transition">Compress PDF</a>
                    <a href="/?tool=convert" class="hover:text-[#e5322b] transition">Convert Studio</a>
                    <a href="/" class="text-[#e5322b] border-b-2 border-[#e5322b] pb-1">All Tools</a>
                </nav>
            </div>
            <div class="text-xs font-mono text-gray-400 bg-gray-50 border border-gray-200 px-3 py-1.5 rounded-full">
                UNIVERSAL TWO-WAY MATRIX v5.0
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-8">
            {content}
        </main>

        <footer class="bg-[#161616] text-gray-400 text-center py-6 text-xs border-t border-gray-800">
            <p>&copy; 2026 Free PDF Convert. Real-time Affine scaling and MD5 deduplication processing nodes active.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    # --- ADVANCED CONVERT PDF SUITE HUB ---
    if selected_tool == 'convert':
        convert_html = '''
        <div class="max-w-5xl mx-auto mt-4">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Universal Convert Studio</h1>
                <p class="text-gray-500 text-sm">Two-way formatting pipelines supporting structural orientation shifts and asset deduplication web captures.</p>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col justify-between">
                    <div>
                        <h3 class="text-base font-bold text-gray-900 border-b border-gray-100 pb-2 mb-4">Document & Graphic Transformation</h3>
                        <form method="POST" action="/execute-studio-conversion" enctype="multipart/form-data">
                            <div class="mb-4">
                                <label class="block text-[10px] uppercase font-bold text-gray-400 mb-1">Upload File Target</label>
                                <input type="file" name="file" required class="w-full text-xs text-gray-500 bg-gray-50 p-2 rounded border">
                            </div>
                            <div class="mb-4">
                                <label class="block text-[10px] uppercase font-bold text-gray-400 mb-1">Target Conversion Format Operation</label>
                                <select name="operation" class="w-full bg-gray-50 border p-2 rounded text-xs font-bold text-gray-700">
                                    <option value="pdf2word">Convert PDF to Editable Word (.docx)</option>
                                    <option value="img2pdf_portrait">Convert JPG/PNG to PDF (Forced Portrait View)</option>
                                    <option value="img2pdf_landscape">Convert JPG/PNG to PDF (Forced Landscape View)</option>
                                    <option value="extract_individual_pages">PDF to Images: Convert individual pages to file logs</option>
                                    <option value="extract_embedded_images">PDF to Images: Extract strictly embedded raw graphics</option>
                                </select>
                            </div>
                            <button type="submit" class="w-full bg-[#e5322b] hover:bg-red-700 text-white font-bold py-2.5 rounded-xl uppercase tracking-wider text-xs shadow-md">Execute Conversion Matrix</button>
                        </form>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200 flex flex-col justify-between">
                    <div>
                        <h3 class="text-base font-bold text-gray-900 border-b border-gray-100 pb-2 mb-4">Web Capture Processing Node (HTML to PDF)</h3>
                        <form method="POST" action="/execute-web-capture">
                            <div class="mb-4">
                                <label class="block text-[10px] uppercase font-bold text-gray-400 mb-1">Paste Live Webpage Source HTML or Text Layout</label>
                                <textarea name="html_text" rows="4" required placeholder="Copy and paste your raw HTML code text strings here..." class="w-full bg-gray-50 border p-2 rounded text-xs font-mono focus:outline-none border-gray-200"></textarea>
                            </div>
                            <div class="mb-4 flex items-center space-x-2">
                                <input type="checkbox" name="pdf_a_compliance" id="pdf_a_compliance" class="rounded border-gray-300 text-[#e5322b] focus:ring-[#e5322b]">
                                <label for="pdf_a_compliance" class="text-xs text-gray-500 font-medium cursor-pointer">Enforce strict ISO PDF/A compliance for long-term archiving preservation</label>
                            </div>
                            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-2.5 rounded-xl uppercase tracking-wider text-xs shadow-md">Capture Page Stream</button>
                        </form>
                    </div>
                </div>

            </div>
        </div>
        '''
        return render_layout("Convert Studio", convert_html)

    # --- RENDER ALL OTHER SUITE WORKSPACES ON PATH HOOKS (Merge, Split, Compress) ---
    if selected_tool == 'merge':
        return render_layout("Merge PDF", "<div class='text-center py-20'><p class='text-gray-500 mb-4'>Merge engine configured with safe AcroForm field renaming tags.</p><a href='/?tool=split' class='bg-[#e5322b] px-6 py-3 rounded text-white font-bold text-xs uppercase shadow'>Switch to Split Studio</a></div>")
    if selected_tool == 'split':
        return render_layout("Split PDF", "<div class='text-center py-20'><p class='text-gray-500 mb-4'>Split engine configured to compile multi-page bursts inside ZIP folders.</p><a href='/?tool=compress' class='bg-[#e5322b] px-6 py-3 rounded text-white font-bold text-xs uppercase shadow'>Switch to Compress Studio</a></div>")
    if selected_tool == 'compress':
        return render_layout("Compress PDF", "<div class='text-center py-20'><p class='text-gray-500 mb-4'>Compression suite configured to execute FlateDecode optimizations.</p><a href='/?tool=convert' class='bg-[#e5322b] px-6 py-3 rounded text-white font-bold text-xs uppercase shadow'>Switch to Convert Studio</a></div>")

    # --- MASTER HOMEPAGE SUITE INDEX ---
    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-gray-900 tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">100% free online conversion suite with advanced workspace controls.</p>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-12">
        <a href="/?tool=convert" class="bg-white p-6 rounded-xl shadow-sm border border-red-200 hover:border-[#e5322b] hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Convert PDF Studio</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Execute two-way transitions, pull embedded vector graphic elements, or turn HTML code into structured PDFs.</p>
        </a>
        <a href="/?tool=merge" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF Workspace</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Combine multiple PDFs, manage canvas size variables, and prevent font line skewing safely.</p>
        </a>
    </div>
    '''
    return render_layout("All PDF Tools", grid_html)

@app.route('/execute-studio-conversion', methods=['POST'])
def execute_studio_conversion():
    file = request.files.get('file')
    operation = request.form.get('operation')
    if not file: return "Missing processing asset parameter", 400

    in_path = os.path.join(UPLOAD_FOLDER, "conv_" + file.filename)
    file.save(in_path)

    try:
        if operation == 'pdf2word':
            out_path = os.path.join(UPLOAD_FOLDER, file.filename.replace('.pdf', '.docx'))
            converter_tools.pdf_to_word(in_path, out_path)
            return send_file(out_path, as_attachment=True, download_name="converted_document.docx")
            
        elif operation == 'img2pdf_portrait':
            out_path = os.path.join(UPLOAD_FOLDER, "img_p_" + file.filename + ".pdf")
            converter_tools.img_to_pdf_adjusted(in_path, out_path, orientation="portrait", margins="standard")
            return send_file(out_path, as_attachment=True, download_name="image_portrait.pdf")
            
        elif operation == 'img2pdf_landscape':
            out_path = os.path.join(UPLOAD_FOLDER, "img_l_" + file.filename + ".pdf")
            converter_tools.img_to_pdf_adjusted(in_path, out_path, orientation="landscape", margins="standard")
            return send_file(out_path, as_attachment=True, download_name="image_landscape.pdf")
            
        elif operation == 'extract_individual_pages' or operation == 'extract_embedded_images':
            out_zip = os.path.join(UPLOAD_FOLDER, "extracted_assets_package.zip")
            mode_flag = "pages" if operation == 'extract_individual_pages' else "extract"
            
            extracted_paths = converter_tools.extract_images_or_pages_from_pdf(in_path, mode_flag, UPLOAD_FOLDER)
            if not extracted_paths: return "No valid extractable text or embedded raster image elements detected inside the document tree.", 400
            
            # Pack extracted files into a clean compressed ZIP download
            with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
                for p in extracted_paths:
                    z.write(p, os.path.basename(p))
                    if os.path.exists(p): os.remove(p)
            return send_file(out_zip, as_attachment=True, download_name="extracted_pdf_assets.zip")
            
    except Exception as e:
        return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

@app.route('/execute-web-capture', methods=['POST'])
def execute_web_capture():
    html_markup = request.form.get('html_text', '')
    pdf_a_checked = True if request.form.get('pdf_a_compliance') else False
    if not html_markup: return "Content string parameters empty", 400
    
    out_pdf = os.path.join(UPLOAD_FOLDER, "web_capture_output.pdf")
    try:
        converter_tools.html_web_capture_to_pdf(html_markup, out_pdf, convert_to_pdf_a=pdf_a_checked)
        return send_file(out_pdf, as_attachment=True, download_name="captured_webpage.pdf")
    except Exception as e:
        return str(e), 500
    finally:
        if os.path.exists(out_pdf): os.remove(out_pdf)

if __name__ == '__main__':
    app.run(debug=True)
