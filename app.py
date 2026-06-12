import os
import json
from flask import Flask, request, send_file, render_template_string
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
                    <a href="/" class="text-[#e5322b] border-b-2 border-[#e5322b] pb-1">All PDF Tools</a>
                </nav>
            </div>
            <div class="flex space-x-4 text-sm font-medium text-gray-600">
                <a href="/about" class="hover:text-[#e5322b]">About Us</a>
                <a href="/contact" class="hover:text-[#e5322b]">Contact</a>
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-10">
            {content}
        </main>

        <footer class="bg-[#161616] text-gray-400 text-center py-8 text-xs border-t border-gray-800">
            <div class="flex flex-wrap justify-center space-x-6 mb-4 text-sm font-medium">
                <a href="/about" class="hover:text-white transition">About Us</a>
                <a href="/privacy" class="hover:text-white transition">Privacy Policy</a>
                <a href="/terms" class="hover:text-white transition">Terms & Conditions</a>
                <a href="/contact" class="hover:text-white transition">Contact Us</a>
            </div>
            <p class="text-gray-500">&copy; 2026 Free PDF Convert. Every tool you need to work with PDFs.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    # --- 1. ADVANCED MULTI-FILE VISUAL MERGER INTERFACE ---
    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-5xl mx-auto mt-4">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black text-gray-900 mb-2">Merge PDF Files</h1>
                <p class="text-gray-500 text-sm">Select multiple PDFs, visually view real pages, drag to rearrange, and merge.</p>
            </div>

            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-md border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer relative" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToWorkspace(this.files)">
                    <div class="text-[#e5322b] mb-3 flex justify-center">
                        <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"></path></svg>
                    </div>
                    <p class="text-lg font-bold text-gray-700">Select Multiple PDF Files</p>
                </div>
            </div>

            <div id="workspace-stage" class="hidden bg-white p-8 rounded-2xl shadow-md border border-gray-200">
                <div class="flex justify-between items-center border-b border-gray-200 pb-4 mb-6">
                    <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Drag & Drop Pages to Arrange Order</span>
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold py-2 px-4 rounded-lg transition">+ Add More Files</button>
                </div>
                <div id="pages-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[200px]"></div>
                <div class="mt-8 pt-6 border-t border-gray-200 flex justify-end">
                    <button onclick="submitAdvancedMerge()" id="merge-submit-btn" class="bg-[#e5322b] hover:bg-red-700 text-white font-black py-4 px-10 rounded-xl shadow-lg transition text-lg uppercase tracking-wide">
                        Merge PDF Order
                    </button>
                </div>
            </div>
        </div>

        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
            let filesStorage = [];
            let globalPageMatrix = [];

            async function loadPDFsToWorkspace(files) {
                if (!files.length) return;
                document.getElementById('upload-stage').classList.add('hidden');
                document.getElementById('workspace-stage').classList.remove('hidden');
                const grid = document.getElementById('pages-grid');

                for(let i=0; i<files.length; i++) {
                    let file = files[i];
                    filesStorage.push(file);
                    let fileIdx = filesStorage.length - 1;

                    let fileReader = new FileReader();
                    fileReader.onload = async function() {
                        let typedarray = new Uint8Array(this.result);
                        let pdf = await pdfjsLib.getDocument(typedarray).promise;

                        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                            let pageId = "item-" + fileIdx + "-" + (pageNum - 1);
                            globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1 });

                            let card = document.createElement('div');
                            card.id = pageId;
                            card.className = "bg-white border-2 border-gray-200 p-3 rounded-xl shadow-sm cursor-move relative select-none hover:border-[#e5322b] transition flex flex-col justify-between";
                            card.draggable = true;
                            
                            let canvas = document.createElement('canvas');
                            canvas.className = "w-full rounded bg-gray-100 border border-gray-200 aspect-[3/4]";
                            card.appendChild(canvas);

                            let infoRow = document.createElement('div');
                            infoRow.className = "flex justify-between items-center text-xs mt-2 text-gray-500";
                            infoRow.innerHTML = '<span class="font-bold index-marker">#' + (grid.children.length + 1) + '</span><span class="truncate max-w-[70px] text-[10px] bg-gray-100 px-1 py-0.5 rounded">' + file.name + '</span><button type="button" onclick="this.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">X</button>';
                            card.appendChild(infoRow);
                            grid.appendChild(card);

                            renderThumb(pdf, pageNum, canvas);
                            card.addEventListener('dragstart', (e) => e.dataTransfer.setData('text/plain', card.id));
                        }
                        setupDragAndDrop();
                    };
                    fileReader.readAsArrayBuffer(file);
                }
            }

            async function renderThumb(pdfInstance, pageNum, canvasElement) {
                let page = await pdfInstance.getPage(pageNum);
                let viewport = page.getViewport({ scale: 0.2 });
                let context = canvasElement.getContext('2d');
                canvasElement.height = viewport.height;
                canvasElement.width = viewport.width;
                page.render({ canvasContext: context, viewport: viewport });
            }

            function setupDragAndDrop() {
                const grid = document.getElementById('pages-grid');
                grid.addEventListener('dragover', (e) => e.preventDefault());
                grid.addEventListener('drop', (e) => {
                    e.preventDefault();
                    const draggedId = e.dataTransfer.getData('text/plain');
                    const draggedElement = document.getElementById(draggedId);
                    const target = e.target.closest('#pages-grid > div');
                    if (draggedElement && target && draggedElement !== target) {
                        const children = Array.from(grid.children);
                        const draggedPos = children.indexOf(draggedElement);
                        const targetPos = children.indexOf(target);
                        if (draggedPos < targetPos) {
                            grid.insertBefore(draggedElement, target.nextSibling);
                        } else {
                            grid.insertBefore(draggedElement, target);
                        }
                        rebuildMatrixSequence();
                    }
                });
            }

            function rebuildMatrixSequence() {
                const grid = document.getElementById('pages-grid');
                const orderCards = Array.from(grid.children);
                let newMatrix = [];
                orderCards.forEach((card, index) => {
                    card.querySelector('.index-marker').textContent = '#' + (index + 1);
                    let parts = card.id.split('-');
                    newMatrix.push({ fileIdx: parseInt(parts[1]), pageIdx: parseInt(parts[2]) });
                });
                globalPageMatrix = newMatrix;
                if(globalPageMatrix.length === 0) window.location.reload();
            }

            function submitAdvancedMerge() {
                if(globalPageMatrix.length === 0) return;
                const btn = document.getElementById('merge-submit-btn');
                btn.disabled = true;
                btn.innerHTML = 'PROCESSING...';
                btn.className = "bg-gray-400 text-white font-black py-4 px-10 rounded-xl cursor-not-allowed text-lg uppercase tracking-wide animate-pulse";

                let formData = new FormData();
                filesStorage.forEach((file, index) => { formData.append("file_" + index, file); });
                formData.append('layout_plan', JSON.stringify(globalPageMatrix.map(item => ({ fileId: "file_" + item.fileIdx, pageIdx: item.pageIdx }))));

                fetch('/execute-advanced-merge', { method: 'POST', body: formData })
                .then(res => res.blob())
                .then(blob => {
                    let url = window.URL.createObjectURL(blob);
                    let a = document.createElement('a');
                    a.href = url;
                    a.download = "merged_document.pdf";
                    document.body.appendChild(a);
                    a.click();
                    window.location.reload();
                });
            }
        </script>
        '''
        return render_layout("Merge PDF", merge_html)

    # --- 2. REGULAR UPLOAD FOR ALL OTHER SINGLE TOOLS ---
    if selected_tool:
        tool_titles = {
            'split': 'Split PDF', 'compress': 'Compress PDF', 'pdf2word': 'PDF to Word',
            'img2pdf': 'Image to PDF', 'repair': 'Repair PDF', 'resize': 'Resize Image', 'enhance': 'Enhance Image'
        }
        title = tool_titles.get(selected_tool, "Document Tool")
        accept_types = "image/*" if selected_tool in ['resize', 'enhance', 'img2pdf'] else ".pdf"

        upload_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-md border border-gray-200 text-center mt-6">
            <h1 class="text-3xl font-black text-gray-900 mb-2">{title}</h1>
            <p class="text-gray-500 text-sm mb-8">Upload your file parameters to begin automatic conversion matrix workflows.</p>
            
            <form method="POST" action="/process-file" enctype="multipart/form-data" onsubmit="showLoading(this)">
                <input type="hidden" name="operation" value="{selected_tool}">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-10 bg-gray-50 hover:bg-red-50/20 transition cursor-pointer relative mb-6">
                    <input type="file" name="file" accept="{accept_types}" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('file-name-display').textContent = 'Selected: ' + this.files[0].name">
                    <div class="text-[#e5322b] mb-3 flex justify-center">
                        <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    </div>
                    <p id="file-name-display" class="text-base font-bold text-gray-700">Select file or drag and drop here</p>
                </div>
                <button type="submit" id="sub-btn" class="w-full bg-[#e5322b] hover:bg-red-700 text-white font-extrabold py-4 px-6 rounded-xl shadow-lg text-lg uppercase tracking-wider transition">
                    Upload & Process
                </button>
            </form>
        </div>
        <script>
            function showLoading(form) {{
                const btn = document.getElementById('sub-btn');
                btn.disabled = true;
                btn.innerHTML = 'PROCESSING...';
                btn.className = "w-full bg-gray-400 text-white font-extrabold py-4 px-6 rounded-xl cursor-not-allowed text-lg uppercase tracking-wider animate-pulse";
            }}
        </script>
        '''
        return render_layout(title, upload_html)

    # --- 3. CLASSIC WHITE MAIN ILOVEPDF GRID LAYOUT ---
    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-gray-900 tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">100% free online document conversion tools and image editors.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-12">
        <a href="/?tool=merge" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Combine multiple PDFs, adjust page sequences visually and merge.</p>
        </a>
        <a href="/?tool=split" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Split PDF</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Extract page scopes down into independent file assets instantly.</p>
        </a>
        <a href="/?tool=compress" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Compress PDF</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Optimize file weight while ensuring maximum text layout output.</p>
        </a>
        <a href="/?tool=pdf2word" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-blue-600 mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-blue-600 mb-1">PDF to Word</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Turn static PDF sheets directly into editable Word .docx files.</p>
        </a>
        <a href="/?tool=img2pdf" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-emerald-600 mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-emerald-600 mb-1">Image to PDF</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Convert JPG or PNG matrix photos into unified printable PDFs.</p>
        </a>
        <a href="/?tool=repair" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-amber-600 mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.907c.961 0 1.36 1.252.588 1.81l-3.97 2.885a1 1 0 00-.364 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.971-2.885a1 1 0 00-1.18 0l-3.97 2.885c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.364-1.118l-3.97-2.885c-.772-.558-.372-1.81.588-1.81h4.906a1 1 0 00.951-.69l1.519-4.674z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-amber-600 mb-1">Repair PDF</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Fix cross-reference cross tables inside corrupted file vectors.</p>
        </a>
        <a href="/?tool=resize" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-purple-600 mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-purple-600 mb-1">Resize Image</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Downsample resolution dimensions by 50% to save storage space.</p>
        </a>
        <a href="/?tool=enhance" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-fuchsia-600 mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-fuchsia-600 mb-1">Enhance Image</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Amplify picture color matrices to maximize clear contrast mapping.</p>
        </a>
    </div>
    '''
    return render_layout("All PDF Tools", grid_html)

@app.route('/execute-advanced-merge', methods=['POST'])
def execute_advanced_merge():
    try:
        plan_data = request.form.get('layout_plan')
        page_order_plan = json.loads(plan_data)
        uploaded_files_map = {}
        saved_paths = []
        for key in request.files:
            file = request.files[key]
            path = os.path.join(UPLOAD_FOLDER, f"m_tmp_{key}_{file.filename}")
            file.save(path)
            uploaded_files_map[key] = path
            saved_paths.append(path)
        out_file = os.path.join(UPLOAD_FOLDER, "merged_output.pdf")
        pdf_tools.merge_advanced_pdf(uploaded_files_map, page_order_plan, out_file)
        return send_file(out_file, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        for p in saved_paths:
            if os.path.exists(p): os.remove(p)

@app.route('/process-file', methods=['POST'])
def process_file():
    operation = request.form.get('operation')
    file = request.files.get('file')
    if not file or file.filename == '': return "Missing File", 400
    in_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(in_path)
    try:
        if operation == 'pdf2word':
            out_path = os.path.join(UPLOAD_FOLDER, file.filename.replace('.pdf', '.docx'))
            converter_tools.pdf_to_word(in_path, out_path)
        elif operation == 'img2pdf':
            out_path = os.path.join(UPLOAD_FOLDER, file.filename + ".pdf")
            converter_tools.img_to_pdf(in_path, out_path)
        elif operation == 'compress':
            out_path = os.path.join(UPLOAD_FOLDER, "compressed_" + file.filename)
            pdf_tools.compress_pdf(in_path, out_path)
        elif operation == 'split':
            out_path = os.path.join(UPLOAD_FOLDER, "split_page1_" + file.filename)
            pdf_tools.split_pdf_first_page(in_path, out_path)
        elif operation == 'repair':
            out_path = os.path.join(UPLOAD_FOLDER, "repaired_" + file.filename)
            pdf_tools.repair_pdf(in_path, out_path)
        elif operation == 'resize':
            out_path = os.path.join(UPLOAD_FOLDER, "resized_" + file.filename)
            image_tools.resize_image(in_path, out_path)
        elif operation == 'enhance':
            out_path = os.path.join(UPLOAD_FOLDER, "enhanced_" + file.filename)
            image_tools.enhance_image(in_path, out_path)
        else: return "Unknown tool", 400
        return send_file(out_path, as_attachment=True)
    except Exception as e: return f"Error: {str(e)}", 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

@app.route('/about')
def page_about(): return render_layout("About Us", "<div class='bg-white p-8 rounded-xl border border-gray-200 shadow-sm'><h1 class='text-2xl font-black mb-4'>About Us</h1><p class='text-gray-600 leading-relaxed'>Free PDF Convert builds fast open source conversion pipelines.</p></div>")
@app.route('/privacy')
def page_privacy(): return render_layout("Privacy", "<div class='bg-white p-8 rounded-xl border border-gray-200 shadow-sm'><h1 class='text-2xl font-black mb-4'>Privacy Policy</h1><p class='text-gray-600 leading-relaxed'>No tracking cookies. Files immediately dump from temporary cache on task finish.</p></div>")
@app.route('/terms')
def page_terms(): return render_layout("Terms", "<div class='bg-white p-8 rounded-xl border border-gray-200 shadow-sm'><h1 class='text-2xl font-black mb-4'>Terms & Conditions</h1><p class='text-gray-600 leading-relaxed'>Services run as-is without internal data payload storage liabilities.</p></div>")
@app.route('/contact')
def page_contact(): return render_layout("Contact", "<div class='bg-white p-8 rounded-xl border border-gray-200 shadow-sm'><h1 class='text-2xl font-black mb-4'>Contact Us</h1><p class='text-gray-600 leading-relaxed'>Email lines: support@freepdfconvert.com</p></div>")

if __name__ == '__main__':
    app.run(debug=True)
