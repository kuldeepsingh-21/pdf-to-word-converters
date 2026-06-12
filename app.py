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
            <p class="text-gray-500">&copy; 2026 Free PDF Convert. Visually arrange, zoom, and rotate document page frameworks.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    # --- ADVANCED MULTI-FILE VISUAL MERGER WITH ROTATE & ZOOM ---
    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-6xl mx-auto mt-4">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black text-gray-900 mb-2">Merge PDF Files</h1>
                <p class="text-gray-500 text-sm">Upload multiple PDFs, adjust layout views (Zoom/Rotate orientation), and merge seamlessly.</p>
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
                <div class="flex flex-col sm:flex-row justify-between items-center border-b border-gray-200 pb-4 mb-6 gap-4">
                    <div class="flex items-center space-x-4">
                        <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Workspace View Toolbar</span>
                        <div class="bg-gray-100 p-1 rounded-lg flex items-center space-x-1 border border-gray-200 shadow-inner">
                            <button onclick="adjustGlobalZoom(-10)" class="px-2 py-1 text-xs font-black text-gray-600 hover:bg-white rounded transition">-</button>
                            <span id="zoom-factor" class="text-xs font-mono px-2 text-gray-700 font-bold">100%</span>
                            <button onclick="adjustGlobalZoom(10)" class="px-2 py-1 text-xs font-black text-gray-600 hover:bg-white rounded transition">+</button>
                        </div>
                    </div>
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold py-2 px-4 rounded-lg border border-gray-300 transition">+ Add More Files</button>
                </div>

                <div id="pages-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[220px] transition-all"></div>

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
            let zoomScale = 100; // Workspace layout scale factor

            // Handle Global Zoom Controls
            function adjustGlobalZoom(amount) {
                zoomScale = Math.max(50, Math.min(200, zoomScale + amount));
                document.getElementById('zoom-factor').textContent = zoomScale + '%';
                
                // Dynamically modify card sizes across workspace view arrays
                const cards = document.querySelectorAll('.canvas-container');
                cards.forEach(card => {
                    card.style.transform = `scale(${zoomScale / 100})`;
                });
            }

            // Individual Page layout rotation mapping
            function rotatePageCard(cardId) {
                const targetCard = document.getElementById(cardId);
                let currentRotation = parseInt(targetCard.getAttribute('data-rotation') || '0');
                currentRotation = (currentRotation + 90) % 360;
                targetCard.setAttribute('data-rotation', currentRotation);
                
                const canvas = targetCard.querySelector('canvas');
                canvas.style.transform = `rotate(${currentRotation}deg)`;
                
                // Toggle visible metadata tagging indicators
                const label = targetCard.querySelector('.layout-label');
                if (currentRotation === 90 || currentRotation === 270) {
                    label.textContent = "Landscape";
                    label.className = "layout-label text-[9px] font-bold bg-amber-100 text-amber-800 px-1 py-0.5 rounded";
                } else {
                    label.textContent = "Portrait";
                    label.className = "layout-label text-[9px] font-bold bg-blue-100 text-blue-800 px-1 py-0.5 rounded";
                }
                rebuildMatrixSequence();
            }

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
                            globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1, rotation: 0 });

                            let card = document.createElement('div');
                            card.id = pageId;
                            card.setAttribute('data-rotation', '0');
                            card.className = "bg-white border-2 border-gray-200 p-3 rounded-xl shadow-sm cursor-move relative select-none hover:border-[#e5322b] transition flex flex-col justify-between overflow-hidden";
                            card.draggable = true;
                            
                            // Wrapping element wrapper to safely scale internal zoom geometries
                            let canvasWrapper = document.createElement('div');
                            canvasWrapper.className = "canvas-container w-full aspect-[3/4] overflow-hidden flex items-center justify-center mb-2 transition-transform origin-center";
                            
                            let canvas = document.createElement('canvas');
                            canvas.className = "w-full rounded bg-gray-100 border border-gray-200 aspect-[3/4] transition-transform duration-200 origin-center";
                            
                            canvasWrapper.appendChild(canvas);
                            card.appendChild(canvasWrapper);

                            let infoRow = document.createElement('div');
                            infoRow.className = "flex justify-between items-center text-xs mt-2 text-gray-500 gap-1";
                            infoRow.innerHTML = `
                                <span class="font-bold index-marker">#${grid.children.length + 1}</span>
                                <span class="layout-label text-[9px] font-bold bg-blue-100 text-blue-800 px-1 py-0.5 rounded">Portrait</span>
                                <button type="button" onclick="rotatePageCard('${pageId}')" class="text-gray-500 hover:text-[#e5322b] bg-gray-100 p-1 rounded font-bold text-[10px]" title="Rotate 90°">⟳ Rotate</button>
                                <button type="button" onclick="this.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold px-1">X</button>
                            `;
                            card.appendChild(infoRow);
                            grid.appendChild(card);

                            renderThumb(pdf, pageNum, canvas);
                            card.addEventListener('dragstart', (e) => e.dataTransfer.setData('text/plain', card.id));
                        }
                        setupDragAndDrop();
                        adjustGlobalZoom(0); // Trigger visual scaling setup alignment
                    };
                    fileReader.readAsArrayBuffer(file);
                }
            }

            async function renderThumb(pdfInstance, pageNum, canvasElement) {
                let page = await pdfInstance.getPage(pageNum);
                let viewport = page.getViewport({ scale: 0.3 });
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
                    let rot = parseInt(card.getAttribute('data-rotation') || '0');
                    newMatrix.push({ fileIdx: parseInt(parts[1]), pageIdx: parseInt(parts[2]), rotation: rot });
                });
                globalPageMatrix = newMatrix;
                if(globalPageMatrix.length === 0) window.location.reload();
            }

            function submitAdvancedMerge() {
                if(globalPageMatrix.length === 0) return;
                const btn = document.getElementById('merge-submit-btn');
                btn.disabled = true;
                btn.innerHTML = 'PROCESSING CHANNELS...';
                btn.className = "bg-gray-400 text-white font-black py-4 px-10 rounded-xl cursor-not-allowed text-lg uppercase tracking-wide animate-pulse";

                let formData = new FormData();
                filesStorage.forEach((file, index) => { formData.append("file_" + index, file); });
                formData.append('layout_plan', JSON.stringify(globalPageMatrix.map(item => ({ 
                    fileId: "file_" + item.fileIdx, 
                    pageIdx: item.pageIdx,
                    rotation: item.rotation 
                }))));

                fetch('/execute-advanced-merge', { method: 'POST', body: formData })
                .then(res => res.blob())
                .then(blob => {
                    let url = window.URL.createObjectURL(blob);
                    let a = document.createElement('a');
                    a.href = url;
                    a.download = "organized_document.pdf";
                    document.body.appendChild(a);
                    a.click();
                    window.location.reload();
                });
            }
        </script>
        '''
        return render_layout("Merge PDF", merge_html)

    # --- MAIN GRID HOME DASHBOARD ---
    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-gray-900 tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">100% free online conversion suite with advanced workspace controls.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-12">
        <a href="/?tool=merge" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF Workspace</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Combine multiple PDFs, adjust rotations, manage page scale zoom factors, and merge.</p>
        </a>
        <a href="/?tool=pdf2word" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-blue-600 mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-blue-600 mb-1">PDF to Word</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Turn static PDF sheets directly into editable Word .docx profiles.</p>
        </a>
        <a href="/?tool=compress" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Compress PDF</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Optimize file weight while ensuring maximum text layout output.</p>
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
        elif operation == 'compress':
            out_path = os.path.join(UPLOAD_FOLDER, "compressed_" + file.filename)
            pdf_tools.compress_pdf(in_path, out_path)
        else: return "Unknown tool", 400
        return send_file(out_path, as_attachment=True)
    except Exception as e: return f"Error: {str(e)}", 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

if __name__ == '__main__':
    app.run(debug=True)
