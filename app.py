import os
import json
from flask import Flask, request, send_file
import pdf_tools

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'

def render_layout(title, content):
    return f'''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{title} - Free PDF Pro Engine</title>
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
                    <a href="/?tool=merge" class="text-[#e5322b] border-b-2 border-[#e5322b] pb-1">Merge PDF Workspace</a>
                </nav>
            </div>
            <div class="text-xs font-mono text-gray-500 bg-gray-100 px-3 py-1.5 rounded-full border border-gray-200">
                MATRIX TRANSFORMATION LAYOUT FLOW
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-8">
            {content}
        </main>

        <footer class="bg-[#161616] text-gray-500 text-center py-6 text-xs">
            <p>&copy; 2026 Free PDF Convert. Advanced layout-scaling matrix operational pipeline.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-7xl mx-auto">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Advanced Layout Setup Workspace</h1>
                <p class="text-gray-500 text-sm">Natively parses Landscape inputs, injects content-safe auto-scaling containers, and provides deep full-screen magnification.</p>
            </div>

            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToSetupWorkspace(this.files)">
                    <div class="text-[#e5322b] mb-3 flex justify-center">
                        <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4v16m8-8H4"></path></svg>
                    </div>
                    <p class="text-base font-bold text-gray-700">Select Multiple PDF Files</p>
                </div>
            </div>

            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-200 pb-4 mb-6 gap-4">
                    
                    <div class="flex flex-wrap items-center gap-4 w-full md:w-auto">
                        <div class="flex flex-col">
                            <label class="text-[10px] uppercase font-bold text-gray-400 mb-1 tracking-wider">Output Dimensions Target</label>
                            <select id="global-size-setup" class="bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 text-xs font-bold text-gray-700 focus:outline-none focus:border-[#e5322b]">
                                <option value="original">Original Size Matrix (Dynamic Auto-Fit)</option>
                                <option value="A4">Standard A4 Size (595 × 842 pt)</option>
                                <option value="LETTER">US Letter Size (612 × 792 pt)</option>
                            </select>
                        </div>
                        
                        <div class="flex flex-col">
                            <label class="text-[10px] uppercase font-bold text-gray-400 mb-1 tracking-wider">Grid Zoom Scale</label>
                            <div class="bg-gray-100 p-1 rounded-lg flex items-center space-x-1 border border-gray-200 h-8">
                                <button onclick="adjustWorkspaceZoom(-10)" class="px-2.5 text-xs font-black text-gray-600 hover:bg-white rounded transition">-</button>
                                <span id="zoom-value" class="text-xs font-mono px-2 text-gray-700 font-bold">100%</span>
                                <button onclick="adjustWorkspaceZoom(10)" class="px-2.5 text-xs font-black text-gray-600 hover:bg-white rounded transition">+</button>
                            </div>
                        </div>
                    </div>
                    
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold py-2.5 px-4 rounded-lg border border-gray-300 transition shrink-0">+ Add Extra Documents</button>
                </div>

                <div id="pages-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[220px]"></div>

                <div class="mt-8 pt-4 border-t border-gray-200 flex justify-end">
                    <button onclick="submitPageSetupMerge()" id="merge-submit-btn" class="bg-[#e5322b] hover:bg-red-700 text-white font-black py-4 px-12 rounded-xl shadow-lg transition text-md uppercase tracking-wide">
                        Compile & Safely Scale PDF
                    </button>
                </div>
            </div>
        </div>

        <div id="inspector-modal" class="hidden fixed inset-0 bg-black/80 z-50 backdrop-blur-sm flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl w-full max-w-4xl h-[85vh] flex flex-col justify-between shadow-2xl relative animate-in fade-in duration-200">
                <div class="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50 rounded-t-2xl">
                    <h3 id="inspector-title" class="text-sm font-bold text-gray-700 truncate max-w-md">Document Inspector Viewport</h3>
                    <button onclick="closeInspectorModal()" class="bg-gray-200 hover:bg-red-600 hover:text-white text-gray-700 font-black px-3 py-1.5 rounded-lg transition text-xs">✕ Close Size</button>
                </div>
                <div class="flex-grow p-4 overflow-auto bg-gray-100 flex items-center justify-center">
                    <canvas id="inspector-canvas" class="max-w-full max-h-full shadow-md rounded bg-white object-contain"></canvas>
                </div>
                <div id="inspector-footer" class="p-3 border-t border-gray-200 text-center text-xs font-mono text-gray-400 bg-gray-50 rounded-b-2xl">
                    Resolution Scale Matrix Adjusted to Native Device DPI
                </div>
            </div>
        </div>

        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
            let filesStorage = [];
            let globalPageMatrix = [];
            let currentZoom = 100;
            let loadedDocsMap = {};

            function adjustWorkspaceZoom(val) {
                currentZoom = Math.max(60, Math.min(160, currentZoom + val));
                document.getElementById('zoom-value').textContent = currentZoom + '%';
                const containers = document.querySelectorAll('.canvas-viewport-box');
                containers.forEach(box => {{ box.style.transform = `scale(${currentZoom / 100})`; }});
            }

            function openInspectorModal(fileId, pageNum) {{
                const modal = document.getElementById('inspector-modal');
                const canvas = document.getElementById('inspector-canvas');
                const title = document.getElementById('inspector-title');
                
                modal.classList.remove('hidden');
                title.textContent = `Inspecting Page ${pageNum} of Asset Frame Node: [${fileId}]`;
                
                let pdfDoc = loadedDocsMap[fileId];
                if (!pdfDoc) return;
                
                pdfDoc.getPage(pageNum).then(page => {{
                    let ctx = canvas.getContext('2d');
                    let viewport = page.getViewport({{ scale: 1.5 }});
                    canvas.height = viewport.height;
                    canvas.width = viewport.width;
                    page.render({{ canvasContext: ctx, viewport: viewport }});
                }});
            }}

            function closeInspectorModal() {{
                document.getElementById('inspector-modal').classList.add('hidden');
            }}

            function toggleCardLayoutSetup(cardId, val) {
                const targetCard = document.getElementById(cardId);
                targetCard.setAttribute('data-layout', val);
                const canvasBox = targetCard.querySelector('.canvas-viewport-box');
                
                if(val === "landscape") {
                    canvasBox.className = "canvas-viewport-box w-full aspect-[4/3] overflow-hidden bg-white border border-gray-300 rounded shadow-inner flex items-center justify-center origin-center transition-all duration-150";
                } else {
                    canvasBox.className = "canvas-viewport-box w-full aspect-[3/4] overflow-hidden bg-white border border-gray-300 rounded shadow-inner flex items-center justify-center origin-center transition-all duration-150";
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
                    let fileKey = "file_" + fileIdx;

                    let fileReader = new FileReader();
                    fileReader.onload = async function() {
                        let typedarray = new Uint8Array(this.result);
                        let pdf = await pdfjsLib.getDocument(typedarray).promise;
                        loadedDocsMap[fileKey] = pdf;

                        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                            let pageId = "item-" + fileIdx + "-" + (pageNum - 1);
                            let page = await pdf.getPage(pageNum);
                            let nativeViewport = page.getViewport({ scale: 1.0 });
                            
                            // 1. ORIGINAL LANDSCAPE AUTO-DETECTION MATRIX
                            let initialLayout = "portrait";
                            if (nativeViewport.width > nativeViewport.height) {
                                initialLayout = "landscape";
                            }
                            
                            globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1, layout: initialLayout });

                            let card = document.createElement('div');
                            card.id = pageId;
                            card.setAttribute('data-layout', initialLayout);
                            card.className = "bg-white border border-gray-200 p-3 rounded-xl shadow-sm cursor-move select-none hover:border-[#e5322b] transition flex flex-col justify-between overflow-hidden gap-3 group relative";
                            card.draggable = true;
                            
                            let aspectClass = (initialLayout === "landscape") ? "aspect-[4/3]" : "aspect-[3/4]";
                            
                            let canvasBox = document.createElement('div');
                            canvasBox.className = `canvas-viewport-box w-full ${aspectClass} overflow-hidden bg-white border border-gray-300 rounded shadow-inner flex items-center justify-center origin-center transition-all duration-150 relative`;
                            
                            // High-Tech Big Full Size Inspect Button Layer Overlay
                            let overlayBtn = document.createElement('button');
                            overlayBtn.type = "button";
                            overlayBtn.className = "absolute inset-0 bg-black/40 text-white font-bold opacity-0 group-hover:opacity-100 flex items-center justify-center text-xs tracking-wider uppercase transition rounded z-10 font-sans";
                            overlayBtn.innerHTML = "🔍 View Full Size";
                            overlayBtn.onclick = (e) => { e.stopPropagation(); openInspectorModal(fileKey, pageNum); };
                            canvasBox.appendChild(overlayBtn);
                            
                            let canvas = document.createElement('canvas');
                            canvas.className = "w-full h-full object-contain pointer-events-none";
                            canvasBox.appendChild(canvas);
                            card.appendChild(canvasBox);

                            let controlRow = document.createElement('div');
                            controlRow.className = "flex flex-col gap-1.5 text-xs border-t border-gray-100 pt-2.5 z-20 relative";
                            controlRow.innerHTML = `
                                <div class="flex justify-between items-center text-gray-500">
                                    <span class="font-bold index-lbl">#\${grid.children.length + 1}</span>
                                    <span class="truncate max-w-[80px] text-[10px] bg-gray-100 px-1 py-0.5 rounded">\${file.name}</span>
                                    <button type="button" onclick="this.parentElement.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">X</button>
                                </div>
                                <div class="flex items-center justify-between gap-1">
                                    <label class="text-[9px] text-gray-400 font-mono uppercase">Setup Page:</label>
                                    <select onchange="toggleCardLayoutSetup('\${pageId}', this.value)" class="bg-gray-50 border border-gray-200 rounded px-1 py-0.5 text-[11px] font-bold text-gray-700 focus:outline-none focus:border-[#e5322b]">
                                        <option value="portrait" \${initialLayout === "portrait" ? "selected" : ""}>Portrait</option>
                                        <option value="landscape" \${initialLayout === "landscape" ? "selected" : ""}>Landscape</option>
                                    </select>
                                </div>
                            `;
                            card.appendChild(controlRow);
                            grid.appendChild(card);

                            let context = canvas.getContext('2d');
                            let thumbViewport = page.getViewport({ scale: 0.25 });
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
                        if (draggedPos < targetPos) { grid.insertBefore(draggedElement, target.nextSibling); }
                        else { grid.insertBefore(draggedElement, target); }
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
                const sizeSetup = document.getElementById('global-size-setup').value;
                btn.disabled = true;
                btn.innerHTML = 'RE-SCALING CONTROLS & COMPILING...';
                btn.className = "bg-gray-400 text-white font-black py-4 px-12 rounded-xl cursor-not-allowed text-md uppercase tracking-wide animate-pulse";

                let formData = new FormData();
                filesStorage.forEach((file, index) => { formData.append("file_" + index, file); });
                formData.append('global_size_setup', sizeSetup);
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
                    a.download = "pro_setup_scaled_document.pdf";
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
        size_setup = request.form.get('global_size_setup', 'original')
        page_order_plan = json.loads(plan_data)
        uploaded_files_map = {}
        saved_paths = []
        for key in request.files:
            file = request.files[key]
            path = os.path.join(UPLOAD_FOLDER, f"m_setup_{key}_{file.filename}")
            file.save(path)
            uploaded_files_map[key] = path
            saved_paths.append(path)
        out_file = os.path.join(UPLOAD_FOLDER, "normalized_merged_output.pdf")
        
        # Injects dimension targeting parameters safely into the pipeline
        pdf_tools.merge_with_affine_scaling(uploaded_files_map, page_order_plan, size_setup, out_file)
        
        return send_file(out_file, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        for p in saved_paths:
            if os.path.exists(p): os.remove(p)

if __name__ == '__main__':
    app.run(debug=True)
