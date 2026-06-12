import os
import json
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
                    <a href="/?tool=pdf2word" class="hover:text-[#e5322b] transition">Convert PDF</a>
                </nav>
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-8">
            {content}
        </main>

        <footer class="bg-[#161616] text-gray-400 text-center py-6 text-xs">
            <p>&copy; 2026 Free PDF Convert. Secure sandbox compression engines enabled.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    # --- ADVANCED MERGE PDF WORKSPACE ---
    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Merge PDF Workspace</h1>
                <p class="text-gray-500 text-sm">Combine files without overwriting form entries or dropping landscape parameters.</p>
            </div>
            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToSetupWorkspace(this.files)">
                    <p class="text-base font-bold text-gray-700">Select Multiple PDF Files</p>
                </div>
            </div>
            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                <div class="flex flex-col md:flex-row justify-between items-center border-b border-gray-200 pb-4 mb-6 gap-4">
                    <select id="global-size-setup" class="bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 text-xs font-bold text-gray-700"><option value="original">Original Sizing Matrix</option><option value="A4">Standard A4 Canvas</option><option value="LETTER">US Letter Canvas</option></select>
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-100 text-gray-700 text-xs font-bold py-2 px-4 rounded-lg border border-gray-300 transition">+ Add Files</button>
                </div>
                <div id="pages-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[200px]"></div>
                <div class="mt-8 pt-4 border-t border-gray-200 flex justify-end">
                    <button onclick="submitPageSetupMerge()" id="merge-submit-btn" class="bg-[#e5322b] hover:bg-red-700 text-white font-black py-4 px-12 rounded-xl shadow-lg text-md uppercase">Compile & Merge PDF</button>
                </div>
            </div>
        </div>
        ''' + self_contained_javascript_logic()
        return render_layout("Merge PDF", merge_html)

    # --- ADVANCED COMPRESS PDF LEVEL ENGINE MODULE ---
    if selected_tool == 'compress':
        compress_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-md border border-gray-200 mt-6">
            <div class="text-center mb-6">
                <h1 class="text-2xl font-black text-gray-900 mb-1">Compress PDF Engine</h1>
                <p class="text-xs text-gray-500">Reduce file size using FlateDecode stream compression and DPI image resampling algorithms.</p>
            </div>
            
            <form method="POST" action="/execute-asynchronous-compression" enctype="multipart/form-data" onsubmit="document.getElementById('sub-btn').disabled=true; document.getElementById('sub-btn').textContent='RUNNING DOWN-SAMPLING LOGIC...';">
                
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-8 bg-gray-50 mb-6 text-center relative cursor-pointer">
                    <input type="file" name="file" accept=".pdf" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('fn-dsp').textContent = 'Loaded: ' + this.files[0].name">
                    <p id="fn-dsp" class="text-sm font-bold text-gray-700">Select PDF document to compress</p>
                </div>

                <div class="mb-6">
                    <label class="block text-xs uppercase font-bold text-gray-400 mb-2 tracking-wider">Select Optimization Level</label>
                    <select name="compression_level" class="w-full bg-gray-50 border border-gray-300 rounded-lg p-2.5 text-xs font-bold text-gray-700 focus:outline-none focus:border-[#e5322b]">
                        <option value="basic">Basic Compression (150 DPI - High Quality Preservation)</option>
                        <option value="strong">Strong Compression (72 DPI - Maximum Storage Savings)</option>
                    </select>
                </div>

                <button type="submit" id="sub-btn" class="w-full bg-[#e5322b] hover:bg-red-700 text-white font-extrabold py-3.5 rounded-xl shadow-md uppercase tracking-wider text-sm transition">
                    Optimize File Size
                </button>
            </form>
        </div>
        '''
        return render_layout("Compress PDF Suite", compress_html)

    # --- FALLBACK: DYNAMIC VIEW VERIFICATION DISPLAY PAGE ---
    if request.args.get('original_size'):
        orig = int(request.args.get('original_size'))
        comp = int(request.args.get('compressed_size'))
        savings = round(((orig - comp) / orig) * 100, 1)
        filename = request.args.get('filename', 'output.pdf')
        
        success_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-md border border-green-200 mt-6 text-center">
            <div class="text-green-600 mb-3 flex justify-center">
                <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
            </div>
            <h2 class="text-2xl font-black text-gray-900 mb-1">Compression Complete!</h2>
            <p class="text-xs text-gray-500 mb-6">Your file has been scaled down cleanly using DCTDecode arrays.</p>
            
            <div class="grid grid-cols-3 gap-4 bg-gray-50 p-4 rounded-xl border border-gray-100 font-mono text-xs mb-6">
                <div><p class="text-gray-400 text-[10px] uppercase font-sans font-bold">Original Size</p><p class="text-gray-700 font-bold mt-1">{(orig/1024):.1f} KB</p></div>
                <div><p class="text-gray-400 text-[10px] uppercase font-sans font-bold">New Size</p><p class="text-green-600 font-bold mt-1">{(comp/1024):.1f} KB</p></div>
                <div><p class="text-gray-400 text-[10px] uppercase font-sans font-bold">Total Savings</p><p class="text-blue-600 font-bold mt-1">-{savings}%</p></div>
            </div>

            <a href="/retrieve-compressed-file?file={filename}" class="block w-full bg-green-600 hover:bg-green-700 text-white font-extrabold py-3.5 rounded-xl shadow-md uppercase text-sm tracking-wider">
                Download Compressed PDF
            </a>
        </div>
        '''
        return render_layout("Size Optimization Report", success_html)

    # --- STANDARD SUITE HOMEPAGE GRID LINK ---
    return render_layout("All PDF Tools", "<div class='text-center py-20'><a href='/?tool=compress' class='bg-[#e5322b] px-8 py-4 font-bold rounded-xl text-white shadow-xl hover:bg-red-700 uppercase text-sm tracking-widest'>Launch Compress PDF Suite &rarr;</a></div>")

@app.route('/execute-asynchronous-compression', methods=['POST'])
def execute_asynchronous_compression():
    file = request.files.get('file')
    level = request.form.get('compression_level', 'basic')
    if not file: return "No file resource submitted", 400
    
    in_path = os.path.join(UPLOAD_FOLDER, "comp_in_" + file.filename)
    out_path = os.path.join(UPLOAD_FOLDER, "comp_out_" + file.filename)
    file.save(in_path)
    
    try:
        orig_size = os.path.getsize(in_path)
        pdf_tools.advanced_compress_quantization_engine(in_path, level, out_path)
        comp_size = os.path.getsize(out_path)
        
        # Route processing parameters straight onto our Quality Verification Report template page
        return f'''<script>window.location.href="/?original_size={orig_size}&compressed_size={comp_size}&filename={file.filename}";</script>'''
    except Exception as e:
        return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

@app.route('/retrieve-compressed-file')
def retrieve_compressed_file():
    filename = request.args.get('file', '')
    path = os.path.join(UPLOAD_FOLDER, "comp_out_" + filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True, download_name="optimized_" + filename)
    return "Asset stream lost from temporary runtime buffers.", 404

def self_contained_javascript_logic():
    return '''<script> let filesStorage = []; function submitPageSetupMerge() { document.getElementById('merge-submit-btn').disabled=true; } </script>'''

if __name__ == '__main__':
    app.run(debug=True)
