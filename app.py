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
        <title>{title} - Free PDF Convert Pro</title>
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
                    <a href="/?tool=merge" class="hover:text-[#e5322b] transition">Merge PDF Workspace</a>
                    <a href="/?tool=pdf2word" class="hover:text-[#e5322b] transition">Convert PDF</a>
                    <a href="/?tool=compress" class="hover:text-[#e5322b] transition">Compress Size</a>
                </nav>
            </div>
            <div class="text-xs font-mono text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full border border-gray-200">
                AUTO-DETECT PAGE-SETUP v3.5
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-10">
            {content}
        </main>

        <footer class="bg-[#161616] text-gray-400 text-center py-8 text-xs">
            <p>&copy; 2026 Free PDF Convert. Intelligent aspect-ratio scaling node active.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-6xl mx-auto mt-4">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black text-gray-900 mb-2">Advanced Page Setup & Merger</h1>
                <p class="text-gray-500 text-sm">Upload PDFs. Native layouts auto-detect. Modify setups, change text flow directions, scale views, and compile.</p>
            </div>

            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-md border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer relative" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToSetupWorkspace(this.files)">
                    <div class="text-[#e5322b] mb-3 flex justify-center">
                        <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"></path></svg>
                    </div>
                    <p class="text-lg font-bold text-gray-700">Select Multiple PDF Files</p>
                </div>
            </div>

            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                <div class="flex flex-col sm:flex-row justify-between items-center border-b border-gray-200 pb-4 mb-6 gap-4">
                    <div class="flex items-center space-x-4">
                        <span class="text-xs font-mono tracking-wider text-gray-400 uppercase">Live Canvas Zoom:</span>
                        <div class="bg-gray-100 p-1 rounded-lg flex items-center space-x-1 border border-gray-200">
                            <button onclick="adjustWorkspaceZoom(-15)" class="px-2 py-1 text-xs font-black text-gray-600 hover:bg-white rounded transition">-</button>
                            <span id="zoom-value" class="text-xs font-mono px-2 text-gray-700 font-bold">100%</span>
                            <button onclick="adjustWorkspaceZoom(15)" class="px-2 py-1 text-xs font-black text-gray-600 hover:bg-white rounded transition">+</button>
                        </div>
                    </div>
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold py-2 px-4 rounded-lg border border-gray-300 transition">+ Add More Files</button>
                </div>

                <div id="pages-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-4 bg-gray-50 rounded-xl min-h-[200px]"></div>

                <div class="mt-8 pt-6 border-t border-gray-200 flex justify-end">
                    <button onclick="submitPageSetupMerge()" id="merge-submit-btn" class="bg-[#e5322b] hover:bg-red-700 text-white font-black py-4 px-12 rounded-xl shadow-lg transition text-lg uppercase tracking-wide">
                        Generate & Merge PDF
                    </button>
                </div>
            </div>
        </div>

        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
            let filesStorage = [];
            let globalPageMatrix = [];
            let currentZoom = 100;

            function adjustWorkspaceZoom(val) {
                currentZoom = Math.max(60, Math.min(180, currentZoom + val));
                document.getElementById('zoom-value').textContent = currentZoom + '%';
                
                const containers = document.querySelectorAll('.canvas-viewport-box');
                containers.forEach(box => {
                    box.style.transform = `scale(${currentZoom / 100})`;
                });
            }

            function changePageLayoutSetup(cardId, selectionValue) {
                const targetCard = document.getElementById(cardId);
                targetCard.setAttribute('data-layout', selectionValue);
                
                const canvasBox = targetCard.querySelector('.canvas-viewport-box');
                
                if(selectionValue === "landscape") {
                    canvasBox.className = "canvas-viewport-box w-full aspect-[4/3] overflow-hidden bg-white border border-gray-300 rounded shadow-sm transition-all duration-200 flex items-center justify-center origin-center";
                } else {
                    canvasBox.className = "canvas-viewport-box w-full aspect-[3/4] overflow-hidden bg-white border border-gray-300 rounded shadow-sm transition-all duration-200 flex items-center justify-center origin-center";
                }
                rebuildMatrixSequence();
            }

            async function loadPDFsToSetupWorkspace(files) {
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
                            let page = await pdf.getPage(pageNum);
                            let viewport = page.getViewport({ scale: 1.0 });
                            
                            // AUTO-DETECT ORIENTATION: Find if original page is portrait or landscape
                            let initialLayout = "portrait";
                            if (viewport.width > viewport.height) {
                                initialLayout = "landscape";
                            }
                            
                            globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1, layout: initialLayout });

                            let card = document.createElement('div');
                            card.id = pageId;
                            card.setAttribute('data-layout', initialLayout);
                            card.className = "bg-white border border-gray-200 p-4 rounded-xl shadow-sm cursor-move select-none hover:border-[#e5322b] transition flex flex-col justify-between overflow-hidden gap-4";
                            card.draggable = true;
                            
                            let aspectClass = (initialLayout === "landscape") ? "aspect-[4/3]" : "aspect-[3/4]";
                            let canvasBox = document.createElement('div');
                            canvasBox.className = `canvas-viewport-box w-full ${aspectClass} overflow-hidden bg-white border border-gray-300 rounded shadow-sm flex items-center justify-center origin-center transition-all duration-200`;
                            
                            let canvas = document.createElement('canvas');
                            canvas.className = "w-full h-full object-contain";
                            canvasBox.appendChild(canvas);
                            card.appendChild(canvasBox);

                            let controlRow = document.createElement('div');
                            controlRow.className = "flex flex-col gap-2 text-xs border-t border-gray-100 pt-3";
                            controlRow.innerHTML = `
                                <div class="flex justify-between items-center text-gray-500">
                                    <span class="font-bold index-lbl">#${grid.children.length + 1}</span>
                                    <span class="truncate max-w-[100px] text-[10px] bg-gray-100 px-1 py-0.5 rounded">${file.name}</span>
                                    <button type="button" onclick="this.parentElement.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">Remove</button>
                                </div>
                                <div class="flex items-center justify-between gap-2 mt-1">
                                    <label class="text-[10px] text-gray-400 font-mono uppercase">Page Setup:</label>
                                    <select onchange="changePageLayoutSetup('${pageId}', this.value)" class="bg-gray-50 border border-gray-200 rounded px-1.5 py-1 text-gray-700 font-bold focus:outline-none focus:border-[#e5322b]">
                                        <option value="portrait" ${initialLayout === "portrait" ? "selected" : ""}>Portrait Setup</option>
                                        <option value="landscape" ${initialLayout === "landscape" ? "selected" : ""}>Landscape Setup</option>
                                    </select>
                                </div>
                            `;
                            card.appendChild(controlRow);
                            grid.appendChild(card);

                            // Render visual page content thumbnail onto canvas element
                            let context = canvas.getContext('2d');
                            let thumbViewport = page.getViewport({ scale: 0.3 });
                            canvas.height = thumbViewport.height;
                            canvas.width = thumbViewport.width;
                            page.render({ canvasContext: context, viewport: thumbViewport });

                            card.addEventListener('dragstart', (e) => e.dataTransfer.setData('text/plain', card.id));
                        }
                        setupDragAndDrop();
                        adjustWorkspaceZoom(0);
                    };
                    fileReader.readAsArrayBuffer(file);
                }
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
                    card.querySelector('.index-lbl').textContent = '#' + (index + 1);
                    let parts = card.id.split('-');
                    let layoutSetupValue = card.getAttribute('data-layout') || 'portrait';
                    newMatrix.push({ fileIdx: parseInt(parts[1]), pageIdx: parseInt(parts[2]), layout: layoutSetupValue });
                });
                globalPageMatrix = newMatrix;
                if(globalPageMatrix.length === 0) window.location.reload();
            }

            function submitPageSetupMerge() {
                if(globalPageMatrix.length === 0) return;
                const btn = document.getElementById('merge-submit-btn');
                btn.disabled = true;
                btn.innerHTML = 'CONVERTING TEXT LAYOUTS & MERGING...';
                btn.className = "w-full sm:w-auto bg-gray-400 text-white font-black py-4 px-12 rounded-xl cursor-not-allowed text-lg uppercase tracking-wide animate-pulse";

                let formData = new FormData();
                filesStorage.forEach((file, index) => { formData.append("file_" + index, file); });
                formData.append('layout_plan', JSON.stringify(globalPageMatrix.map(item => ({ 
                    fileId: "file_" + item.fileIdx, 
                    pageIdx: item.pageIdx,
                    layout: item.layout 
                }))));

                fetch('/execute-advanced-merge', { method: 'POST', body: formData })
                .then(res => res.blob())
                .then(blob => {
                    let url = window.URL.createObjectURL(blob);
                    let a = document.createElement('a');
                    a.href = url;
                    a.download = "organized_setup_document.pdf";
                    document.body.appendChild(a);
                    a.click();
                    window.location.reload();
                });
            }
        </script>
        '''
        return render_layout("Merge PDF Workspace", merge_html)

    return render_layout("Universal Hub", "<div class='text-center py-20'><a href='/?tool=merge' class='bg-[#e5322b] px-8 py-4 font-bold rounded-xl text-white shadow-xl hover:bg-red-700 uppercase text-sm tracking-widest'>Launch Page Setup Merger Workspace &rarr;</a></div>")

@app.route('/execute-advanced-merge', methods=['POST'])
def execute_advanced_merge():
    try:
        plan_data = request.form.get('layout_plan')
        page_order_plan = json.loads(plan_data)
        uploaded_files_map = {}
        saved_paths = []
        for key in request.files:
            file = request.files[key]
            path = os.path.join(UPLOAD_FOLDER, f"m_setup_{key}_{file.filename}")
            file.save(path)
            uploaded_files_map[key] = path
            saved_paths.append(path)
        out_file = os.path.join(UPLOAD_FOLDER, "layout_merged_output.pdf")
        
        pdf_tools.merge_with_page_setup(uploaded_files_map, page_order_plan, out_file)
        
        return send_file(out_file, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        for p in saved_paths:
            if os.path.exists(p): os.remove(p)

if __name__ == '__main__':
    app.run(debug=True)
