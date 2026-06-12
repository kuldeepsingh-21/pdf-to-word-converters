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
                    <a href="/" class="text-[#e5322b] border-b-2 border-[#e5322b] pb-1">All Tools</a>
                </nav>
            </div>
            <div class="text-sm font-medium text-gray-600">
                <a href="/about" class="hover:text-[#e5322b]">About Us</a>
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-8">
            {content}
        </main>

        <footer class="bg-[#161616] text-gray-400 text-center py-6 text-xs">
            <p>&copy; 2026 Free PDF Convert. Secure normalized matrix engines active.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    # --- 1. ADVANCED WORKSPACE FOR MERGING & PAGE SETUP ---
    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Merge & Page Setup Workspace</h1>
                <p class="text-gray-500 text-sm">Autodetects landscape files. Customize page boundaries, magnify items, and auto-scale text safely.</p>
            </div>

            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToSetupWorkspace(this.files)">
                    <p class="text-base font-bold text-gray-700">Select Multiple PDF Files</p>
                </div>
            </div>

            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                <div class="flex flex-col md:flex-row justify-between items-start md:items-center border-b border-gray-200 pb-4 mb-6 gap-4">
                    <div class="flex flex-wrap items-center gap-4 w-full md:w-auto">
                        <div class="flex flex-col">
                            <label class="text-[10px] uppercase font-bold text-gray-400 mb-1">Target Page Dimensions</label>
                            <select id="global-size-setup" class="bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 text-xs font-bold text-gray-700 focus:outline-none focus:border-[#e5322b]">
                                <option value="original">Original Sizing Matrix (Dynamic Fit)</option>
                                <option value="A4">Standard A4 Canvas (595 × 842 pt)</option>
                                <option value="LETTER">US Letter Canvas (612 × 792 pt)</option>
                            </select>
                        </div>
                        <div class="flex flex-col">
                            <label class="text-[10px] uppercase font-bold text-gray-400 mb-1">Grid Zoom</label>
                            <div class="bg-gray-100 p-1 rounded-lg flex items-center space-x-1 border border-gray-200 h-8">
                                <button onclick="adjustWorkspaceZoom(-10)" class="px-2 text-xs font-black text-gray-600 hover:bg-white rounded">-</button>
                                <span id="zoom-value" class="text-xs font-mono px-2 text-gray-700 font-bold">100%</span>
                                <button onclick="adjustWorkspaceZoom(10)" class="px-2 text-xs font-black text-gray-600 hover:bg-white rounded">+</button>
                            </div>
                        </div>
                    </div>
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs font-bold py-2 px-4 rounded-lg border border-gray-300 transition">+ Add Files</button>
                </div>

                <div id="pages-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[200px]"></div>

                <div class="mt-8 pt-4 border-t border-gray-200 flex justify-end">
                    <button onclick="submitPageSetupMerge()" id="merge-submit-btn" class="bg-[#e5322b] hover:bg-red-700 text-white font-black py-4 px-12 rounded-xl shadow-lg transition text-md uppercase">
                        Compile & Rescale PDF
                    </button>
                </div>
            </div>
        </div>

        <div id="inspector-modal" class="hidden fixed inset-0 bg-black/80 z-50 backdrop-blur-sm flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl w-full max-w-3xl h-[80vh] flex flex-col justify-between shadow-2xl relative">
                <div class="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50 rounded-t-2xl">
                    <h3 id="inspector-title" class="text-sm font-bold text-gray-700 truncate">Document Inspector Viewport</h3>
                    <button onclick="document.getElementById('inspector-modal').classList.add('hidden')" class="bg-gray-200 hover:bg-red-600 hover:text-white text-gray-700 font-black px-3 py-1 rounded-lg text-xs">✕ Close Size</button>
                </div>
                <div class="flex-grow p-4 overflow-auto bg-gray-100 flex items-center justify-center">
                    <canvas id="inspector-canvas" class="max-w-full max-h-full shadow-md rounded bg-white object-contain"></canvas>
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
                currentZoom = Math.max(60, Math.min(150, currentZoom + val));
                document.getElementById('zoom-value').textContent = currentZoom + '%';
                document.querySelectorAll('.canvas-viewport-box').forEach(box => { box.style.transform = `scale(${currentZoom / 100})`; });
            }

            function openInspectorModal(fileKey, pageNum) {
                const modal = document.getElementById('inspector-modal');
                const canvas = document.getElementById('inspector-canvas');
                modal.classList.remove('hidden');
                document.getElementById('inspector-title').textContent = `Inspecting Page ${pageNum}`;
                
                let pdfDoc = loadedDocsMap[fileKey];
                if (pdfDoc) {
                    pdfDoc.getPage(pageNum).then(page => {
                        let ctx = canvas.getContext('2d');
                        let viewport = page.getViewport({ scale: 1.2 });
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        page.render({ canvasContext: ctx, viewport: viewport });
                    });
                }
            }

            function toggleCardLayoutSetup(cardId, val) {
                const targetCard = document.getElementById(cardId);
                targetCard.setAttribute('data-layout', val);
                const canvasBox = targetCard.querySelector('.canvas-viewport-box');
                canvasBox.className = `canvas-viewport-box w-full overflow-hidden bg-white border border-gray-300 rounded shadow-sm flex items-center justify-center origin-center transition-all ${val === "landscape" ? "aspect-[4/3]" : "aspect-[3/4]"}`;
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
                            
                            // LANDSCAPE AUTO-DETECTION MATRIX
                            let initialLayout = (nativeViewport.width > nativeViewport.height) ? "landscape" : "portrait";
                            globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1, layout: initialLayout });

                            let card = document.createElement('div');
                            card.id = pageId;
                            card.setAttribute('data-layout', initialLayout);
                            card.className = "bg-white border border-gray-200 p-3 rounded-xl shadow-sm cursor-move select-none hover:border-[#e5322b] transition flex flex-col justify-between overflow-hidden gap-3 group relative";
                            card.draggable = true;
                            
                            let aspectClass = (initialLayout === "landscape") ? "aspect-[4/3]" : "aspect-[3/4]";
                            let canvasBox = document.createElement('div');
                            canvasBox.className = `canvas-viewport-box w-full ${aspectClass} overflow-hidden bg-white border border-gray-300 rounded shadow-inner flex items-center justify-center origin-center transition-all relative`;
                            
                            let overlayBtn = document.createElement('button');
                            overlayBtn.type = "button";
                            overlayBtn.className = "absolute inset-0 bg-black/40 text-white font-bold opacity-0 group-hover:opacity-100 flex items-center justify-center text-xs transition rounded z-10";
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
                                    <span class="font-bold index-lbl">#${grid.children.length + 1}</span>
                                    <span class="truncate max-w-[80px] text-[10px] bg-gray-100 px-1 py-0.5 rounded">${file.name}</span>
                                    <button type="button" onclick="this.parentElement.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">X</button>
                                </div>
                                <div class="flex items-center justify-between gap-1">
                                    <label class="text-[9px] text-gray-400 font-mono uppercase">Setup:</label>
                                    <select onchange="toggleCardLayoutSetup('${pageId}', this.value)" class="bg-gray-50 border border-gray-200 rounded px-1 py-0.5 text-[11px] font-bold text-gray-700">
                                        <option value="portrait" ${initialLayout === "portrait" ? "selected" : ""}>Portrait</option>
                                        <option value="landscape" ${initialLayout === "landscape" ? "selected" : ""}>Landscape</option>
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
                let newMatrix = [];
                Array.from(grid.children).forEach((card, index) => {
                    card.querySelector('.index-lbl').textContent = '#' + (index + 1);
                    let parts = card.id.split('-');
                    newMatrix.push({ fileIdx: parseInt(parts[1]), pageIdx: parseInt(parts[2]), layout: card.getAttribute('data-layout') || 'portrait' });
                });
                globalPageMatrix = newMatrix;
                if(globalPageMatrix.length === 0) window.location.reload();
            }

            function submitPageSetupMerge() {
                if(globalPageMatrix.length === 0) return;
                const btn = document.getElementById('merge-submit-btn');
                btn.disabled = true;
                btn.innerHTML = 'COMPILING SCALED VIEWS...';
                btn.className = "bg-gray-400 text-white font-black py-4 px-12 rounded-xl cursor-not-allowed text-md uppercase animate-pulse";

                let formData = new FormData();
                filesStorage.forEach((file, index) => { formData.append("file_" + index, file); });
                formData.append('global_size_setup', document.getElementById('global-size-setup').value);
                formData.append('layout_plan', JSON.stringify(globalPageMatrix.map(item => ({ fileId: "file_" + item.fileIdx, pageIdx: item.pageIdx, layout: item.layout }))));

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

    # --- 2. UPLOAD FOR ALL OTHER CONVERSION CHANNELS ---
    if selected_tool:
        tool_titles = {'split': 'Split PDF', 'compress': 'Compress PDF', 'pdf2word': 'PDF to Word', 'img2pdf': 'Image to PDF', 'repair': 'Repair PDF', 'resize': 'Resize Image', 'enhance': 'Enhance Image'}
        title = tool_titles.get(selected_tool, "Converter Tool")
        accept_types = "image/*" if selected_tool in ['resize', 'enhance', 'img2pdf'] else ".pdf"

        upload_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-md border border-gray-200 text-center mt-6">
            <h1 class="text-3xl font-black text-gray-900 mb-2">{title}</h1>
            <form method="POST" action="/process-file" enctype="multipart/form-data" onsubmit="document.getElementById('sub-btn').disabled=true; document.getElementById('sub-btn').textContent='CONVERTING...';">
                <input type="hidden" name="operation" value="{selected_tool}">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-10 bg-gray-50 mb-6 relative">
                    <input type="file" name="file" accept="{accept_types}" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('fn-dsp').textContent = this.files[0].name">
                    <p id="fn-dsp" class="text-base font-bold text-gray-700">Select file parameter target allocation</p>
                </div>
                <button type="submit" id="sub-btn" class="w-full bg-[#e5322b] hover:bg-red-700 text-white font-extrabold py-4 rounded-xl shadow-md uppercase tracking-wider transition">Process Document</button>
            </form>
        </div>
        '''
        return render_layout(title, upload_html)

    # --- 3. THE COMPLETE MAIN ILOVEPDF HOMEPAGE SUITE ---
    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-gray-900 tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">100% free online conversion suite with advanced workspace controls.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-12">
        <a href="/?tool=merge" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF Workspace</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Combine multiple PDFs, adjust landscape scales, manage full size page zoom, and merge.</p>
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
            <p class="text-gray-500 text-xs leading-relaxed">Turn static PDF sheets directly into editable Word .docx profiles.</p>
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
        pdf_tools.merge_with_affine_scaling(uploaded_files_map, page_order_plan, size_setup, out_file)
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
            out_path = os.path.join(UPLOAD_FOLDER, "split_" + file.filename)
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

if __name__ == '__main__':
    app.run(debug=True)
