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
                    <a href="/?tool=merge" class="hover:text-[#e5322b] transition">Merge PDF</a>
                    <a href="/?tool=split" class="hover:text-[#e5322b] transition">Split PDF (ZIP)</a>
                    <a href="/?tool=compress" class="hover:text-[#e5322b] transition">Compress PDF</a>
                    <a href="/?tool=pdf2word" class="hover:text-[#e5322b] transition">Convert PDF</a>
                    <a href="/" class="text-[#e5322b] border-b-2 border-[#e5322b] pb-1">All Tools</a>
                </nav>
            </div>
            <div class="text-xs font-mono text-gray-400 bg-gray-50 border border-gray-200 px-3 py-1.5 rounded-full">
                QUANTUM ENGINE v4.0 ACTIVE
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-8">
            {content}
        </main>

        <footer class="bg-[#161616] text-gray-400 text-center py-6 text-xs">
            <p>&copy; 2026 Free PDF Convert Pro. High-performance document matrix pipeline.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    # --- 1. MERGE PDF WORKSPACE ---
    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Advanced Merge Studio</h1>
                <p class="text-gray-500 text-sm">Combines files using proportional matrix scaling to protect text layout alignment.</p>
            </div>
            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToWorkspace(this.files)">
                    <p class="text-base font-bold text-gray-700">Select Multiple PDF Files</p>
                </div>
            </div>
            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                <div class="flex justify-between items-center border-b border-gray-200 pb-4 mb-6">
                    <select id="global-size-setup" class="bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 text-xs font-bold text-gray-700"><option value="original">Original Sizing Matrix</option><option value="A4">Standard A4 Canvas</option><option value="LETTER">US Letter Canvas</option></select>
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-100 text-gray-700 text-xs font-bold py-2 px-4 rounded-lg border border-gray-300">+ Add Files</button>
                </div>
                <div id="pages-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[200px]"></div>
                <div class="mt-8 pt-4 border-t border-gray-200 flex justify-end">
                    <button onclick="submitPageSetupMerge()" id="merge-submit-btn" class="bg-[#e5322b] hover:bg-red-700 text-white font-black py-4 px-12 rounded-xl shadow-lg text-md uppercase">Compile & Merge PDF</button>
                </div>
            </div>
        </div>
        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
            let filesStorage = []; let globalPageMatrix = [];
            async function loadPDFsToWorkspace(files) {
                if(!files.length) return;
                document.getElementById('upload-stage').classList.add('hidden');
                document.getElementById('workspace-stage').classList.remove('hidden');
                const grid = document.getElementById('pages-grid');
                for(let i=0; i<files.length; i++) {
                    let file = files[i]; filesStorage.push(file); let fileIdx = filesStorage.length - 1;
                    let fileReader = new FileReader();
                    fileReader.onload = async function() {
                        let typedarray = new Uint8Array(this.result);
                        let pdf = await pdfjsLib.getDocument(typedarray).promise;
                        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                            let pageId = "item-" + fileIdx + "-" + (pageNum - 1);
                            let page = await pdf.getPage(pageNum);
                            let nativeViewport = page.getViewport({ scale: 1.0 });
                            let initialLayout = (nativeViewport.width > nativeViewport.height) ? "landscape" : "portrait";
                            globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1, layout: initialLayout });
                            let card = document.createElement('div'); card.id = pageId; card.setAttribute('data-layout', initialLayout);
                            card.className = "bg-white border border-gray-200 p-3 rounded-xl shadow-sm cursor-move relative transition flex flex-col justify-between overflow-hidden gap-2"; card.draggable = true;
                            let aspectClass = (initialLayout === "landscape") ? "aspect-[4/3]" : "aspect-[3/4]";
                            let canvasBox = document.createElement('div'); canvasBox.className = `w-full ${aspectClass} overflow-hidden bg-white border border-gray-200 rounded flex items-center justify-center`;
                            let canvas = document.createElement('canvas'); canvas.className = "w-full h-full object-contain pointer-events-none";
                            canvasBox.appendChild(canvas); card.appendChild(canvasBox);
                            let controlRow = document.createElement('div'); controlRow.className = "flex flex-col gap-1 text-xs border-t border-gray-100 pt-2";
                            controlRow.innerHTML = `<div class="flex justify-between items-center text-gray-500"><span class="font-bold index-lbl">#${grid.children.length + 1}</span><span class="truncate max-w-[70px] text-[10px] bg-gray-100 px-1 rounded">${file.name}</span><button type="button" onclick="this.parentElement.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">X</button></div>`;
                            card.appendChild(controlRow); grid.appendChild(card);
                            let context = canvas.getContext('2d'); let thumbViewport = page.getViewport({ scale: 0.2 });
                            canvas.height = thumbViewport.height; canvas.width = thumbViewport.width; page.render({ canvasContext: context, viewport: thumbViewport });
                            card.addEventListener('dragstart', (e) => e.dataTransfer.setData('text/plain', card.id));
                        }
                        setupDragAndDrop();
                    };
                    fileReader.readAsArrayBuffer(file);
                }
            }
            function setupDragAndDrop() {
                const grid = document.getElementById('pages-grid'); grid.addEventListener('dragover', (e) => e.preventDefault());
                grid.addEventListener('drop', (e) => {
                    e.preventDefault(); const draggedId = e.dataTransfer.getData('text/plain'); const draggedElement = document.getElementById(draggedId);
                    const target = e.target.closest('#pages-grid > div');
                    if (draggedElement && target && draggedElement !== target) {
                        const children = Array.from(grid.children); const draggedPos = children.indexOf(draggedElement); const targetPos = children.indexOf(target);
                        if (draggedPos < targetPos) { grid.insertBefore(draggedElement, target.nextSibling); } else { grid.insertBefore(draggedElement, target); }
                        rebuildMatrixSequence();
                    }
                });
            }
            function rebuildMatrixSequence() {
                const grid = document.getElementById('pages-grid'); let newMatrix = [];
                Array.from(grid.children).forEach((card, index) => {
                    card.querySelector('.index-lbl').textContent = '#' + (index + 1); let parts = card.id.split('-');
                    newMatrix.push({ fileIdx: parseInt(parts[1]), pageIdx: parseInt(parts[2]), layout: card.getAttribute('data-layout') || 'portrait' });
                });
                globalPageMatrix = newMatrix; if(globalPageMatrix.length === 0) window.location.reload();
            }
            function submitPageSetupMerge() {
                const btn = document.getElementById('merge-submit-btn'); btn.disabled = true; btn.innerHTML = 'PROCESSING...';
                let formData = new FormData(); filesStorage.forEach((file, index) => { formData.append("file_" + index, file); });
                formData.append('global_size_setup', document.getElementById('global-size-setup').value);
                formData.append('layout_plan', JSON.stringify(globalPageMatrix.map(item => ({ fileId: "file_" + item.fileIdx, pageIdx: item.pageIdx, layout: item.layout }))));
                fetch('/execute-advanced-merge', { method: 'POST', body: formData }).then(res => res.blob()).then(blob => {
                    let url = window.URL.createObjectURL(blob); let a = document.createElement('a'); a.href = url; a.download = "merged_document.pdf"; a.click(); window.location.reload();
                });
            }
        </script>
        '''
        return render_layout("Merge PDF", merge_html)

    # --- 2. SPLIT PDF WORKSPACE (NEW HIGH-TECH ZIP STREAM OUT) ---
    if selected_tool == 'split':
        split_html = '''
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Visual Split Studio (ZIP Archive Export)</h1>
                <p class="text-gray-500 text-sm">Explode file pages visually, discard unwanted files, rearrange order matrix data, and package cleanly into a fast ZIP file.</p>
            </div>
            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('split-file').click()">
                    <input type="file" id="split-file" accept=".pdf" class="hidden" onchange="loadPDFToSplitWorkspace(this.files[0])">
                    <p class="text-base font-bold text-gray-700">Select PDF File to Extract</p>
                </div>
            </div>
            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                <div class="flex justify-between items-center border-b border-gray-200 pb-4 mb-6">
                    <span class="text-xs font-bold text-gray-500 uppercase tracking-wider">Visual Page Array Extraction Manager</span>
                    <span id="page-count-display" class="text-xs font-mono font-bold bg-red-50 text-[#e5322b] px-2 py-1 rounded">0 Pages Loaded</span>
                </div>
                <div id="pages-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[200px]"></div>
                <div class="mt-8 pt-4 border-t border-gray-200 flex justify-end">
                    <button onclick="submitVisualSplit()" id="split-submit-btn" class="bg-[#e5322b] hover:bg-red-700 text-white font-black py-4 px-12 rounded-xl shadow-lg transition text-md uppercase">
                        Extract & Download ZIP
                    </button>
                </div>
            </div>
        </div>
        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
            let targetSplitFile = null; let globalPageMatrix = [];
            async function loadPDFToSplitWorkspace(file) {
                if (!file) return; targetSplitFile = file;
                document.getElementById('upload-stage').classList.add('hidden'); document.getElementById('workspace-stage').classList.remove('hidden');
                const grid = document.getElementById('pages-grid'); grid.innerHTML = "";
                let fileReader = new FileReader();
                fileReader.onload = async function() {
                    let typedarray = new Uint8Array(this.result);
                    let pdf = await pdfjsLib.getDocument(typedarray).promise;
                    document.getElementById('page-count-display').textContent = `${pdf.numPages} Pages Loaded`;
                    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                        let pageId = `page-node-${pageNum - 1}`; let page = await pdf.getPage(pageNum);
                        let nativeViewport = page.getViewport({ scale: 1.0 });
                        let pageOrientation = (nativeViewport.width > nativeViewport.height) ? "landscape" : "portrait";
                        globalPageMatrix.push({ pageIdx: pageNum - 1 });
                        let card = document.createElement('div'); card.id = pageId;
                        card.className = "bg-white border border-gray-200 p-3 rounded-xl shadow-sm cursor-move relative transition flex flex-col justify-between overflow-hidden gap-2"; card.draggable = true;
                        let aspectClass = (pageOrientation === "landscape") ? "aspect-[4/3]" : "aspect-[3/4]";
                        let canvasBox = document.createElement('div'); canvasBox.className = `w-full ${aspectClass} overflow-hidden bg-white border border-gray-200 rounded flex items-center justify-center`;
                        let canvas = document.createElement('canvas'); canvas.className = "w-full h-full object-contain pointer-events-none";
                        canvasBox.appendChild(canvas); card.appendChild(canvasBox);
                        let metaRow = document.createElement('div'); metaRow.className = "flex justify-between items-center text-xs text-gray-500 pt-1 border-t border-gray-100";
                        metaRow.innerHTML = `<span class="font-bold index-lbl">#${grid.children.length + 1}</span><span class="text-[10px] font-mono text-gray-400">Page ${pageNum}</span><button type="button" onclick="this.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">Delete</button>`;
                        card.appendChild(metaRow); grid.appendChild(card);
                        let context = canvas.getContext('2d'); let thumbViewport = page.getViewport({ scale: 0.2 });
                        canvas.height = thumbViewport.height; canvas.width = thumbViewport.width; page.render({ canvasContext: context, viewport: thumbViewport });
                        card.draggable = true; card.addEventListener('dragstart', (e) => e.dataTransfer.setData('text/plain', card.id));
                    }
                    setupDragAndDrop();
                };
                fileReader.readAsArrayBuffer(file);
            }
            function setupDragAndDrop() {
                const grid = document.getElementById('pages-grid'); grid.addEventListener('dragover', (e) => e.preventDefault());
                grid.addEventListener('drop', (e) => {
                    e.preventDefault(); const draggedId = e.dataTransfer.getData('text/plain'); const draggedElement = document.getElementById(draggedId);
                    const target = e.target.closest('#pages-grid > div');
                    if (draggedElement && target && draggedElement !== target) {
                        const children = Array.from(grid.children); const draggedPos = children.indexOf(draggedElement); const targetPos = children.indexOf(target);
                        if (draggedPos < targetPos) { grid.insertBefore(draggedElement, target.nextSibling); } else { grid.insertBefore(draggedElement, target); }
                        rebuildMatrixSequence();
                    }
                });
            }
            function rebuildMatrixSequence() {
                const grid = document.getElementById('pages-grid'); let newMatrix = [];
                Array.from(grid.children).forEach((card, index) => {
                    card.querySelector('.index-lbl').textContent = '#' + (index + 1); let parts = card.id.split('-');
                    newMatrix.push({ pageIdx: parseInt(parts[2]) });
                });
                globalPageMatrix = newMatrix; document.getElementById('page-count-display').textContent = `${globalPageMatrix.length} Pages Retained`;
                if(globalPageMatrix.length === 0) window.location.reload();
            }
            function submitVisualSplit() {
                const btn = document.getElementById('split-submit-btn'); btn.disabled = true; btn.innerHTML = 'PACKAGING ZIP...';
                let formData = new FormData(); formData.append("file", targetSplitFile);
                formData.append('split_plan', JSON.stringify(globalPageMatrix.map(item => item.pageIdx)));
                fetch('/execute-visual-split', { method: 'POST', body: formData }).then(res => res.blob()).then(blob => {
                    let url = window.URL.createObjectURL(blob); let a = document.createElement('a'); a.href = url; a.download = "extracted_pages.zip"; a.click(); window.location.reload();
                });
            }
        </script>
        '''
        return render_layout("Split PDF", split_html)

    # --- 3. GENERIC SINGLE FILE LOADER SYSTEM ---
    if selected_tool:
        tool_titles = {'compress': 'Compress PDF Engine', 'pdf2word': 'PDF to Word Converter', 'img2pdf': 'Image to PDF Converter', 'repair': 'PDF Structural Repair Tool', 'resize': 'Image Resolution Sizer', 'enhance': 'Image Contrast Enhancer'}
        title = tool_titles.get(selected_tool, "Converter Processing Module")
        accept_types = "image/*" if selected_tool in ['resize', 'enhance', 'img2pdf'] else ".pdf"
        upload_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-md border border-gray-200 text-center mt-6">
            <h1 class="text-2xl font-black text-gray-900 mb-2">{title}</h1>
            <p class="text-sm text-gray-500 mb-6">Upload your target object asset layer to execute pipeline computations.</p>
            <form method="POST" action="/process-file" enctype="multipart/form-data" onsubmit="document.getElementById('sub-btn').disabled=true; document.getElementById('sub-btn').textContent='PROCESSING AUTOMATION...';">
                <input type="hidden" name="operation" value="{selected_tool}">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-10 bg-gray-50 mb-6 relative">
                    <input type="file" name="file" accept="{accept_types}" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('fn-dsp').textContent = this.files[0].name">
                    <p id="fn-dsp" class="text-base font-bold text-gray-700">Select file parameter target allocation</p>
                </div>
                <button type="submit" id="sub-btn" class="w-full bg-[#e5322b] hover:bg-red-700 text-white font-extrabold py-4 rounded-xl shadow-md uppercase tracking-wider text-sm">Process Data</button>
            </form>
        </div>
        '''
        return render_layout(title, upload_html)

    # --- 4. PREMIUM RED/WHITE iLOVEPDF CORE GRID LAYOUT ---
    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-gray-900 tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">100% free online conversion suite with advanced workspace controls.</p>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-12">
        <a href="/?tool=merge" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF Workspace</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Combine multiple PDFs, adjust landscape scales, and merge document sequences.</p>
        </a>
        <a href="/?tool=split" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Split PDF (ZIP out)</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Explode pages visually, remove frames, rearrange order, and compress into ZIP.</p>
        </a>
        <a href="/?tool=compress" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Compress PDF Suite</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Advanced stream-content quantization reduction to scale file sizes down safely.</p>
        </a>
        <a href="/?tool=pdf2word" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-blue-600 mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-blue-600 mb-1">PDF to Word Converter</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Turn static PDF sheets directly into editable Word .docx profiles.</p>
        </a>
        <a href="/?tool=img2pdf" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-emerald-600 mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-emerald-600 mb-1">Image to PDF Matrix</h3>
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
        uploaded_files_map = {} ; saved_paths = []
        for key in request.files:
            file = request.files[key]
            path = os.path.join(UPLOAD_FOLDER, f"m_setup_{key}_{file.filename}")
            file.save(path) ; uploaded_files_map[key] = path ; saved_paths.append(path)
        out_file = os.path.join(UPLOAD_FOLDER, "normalized_merged_output.pdf")
        pdf_tools.merge_with_affine_scaling(uploaded_files_map, page_order_plan, size_setup, out_file)
        return send_file(out_file, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        for p in saved_paths:
            if os.path.exists(p): os.remove(p)

@app.route('/execute-visual-split', methods=['POST'])
def execute_visual_split():
    file = request.files.get('file')
    plan_data = request.form.get('split_plan')
    if not file or not plan_data: return "Missing Parameters", 400
    in_path = os.path.join(UPLOAD_FOLDER, "split_in_" + file.filename)
    out_zip = os.path.join(UPLOAD_FOLDER, "split_out_archive.zip")
    file.save(in_path)
    try:
        page_indices_list = json.loads(plan_data)
        # Call the high-tech backend ZIP packager engine
        pdf_tools.split_pdf_into_zip_archive(in_path, page_indices_list, out_zip)
        return send_file(out_zip, as_attachment=True, download_name="extracted_pages.zip")
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)
        if os.path.exists(out_zip): os.remove(out_zip)

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
            pdf_tools.high_tech_compress_quantization(in_path, out_path)
        elif operation == 'repair':
            out_path = os.path.join(UPLOAD_FOLDER, "repaired_" + file.filename)
            pdf_tools.repair_pdf(in_path, out_path)
        elif operation == 'resize':
            out_path = os.path.join(UPLOAD_FOLDER, "resized_" + file.filename)
            image_tools.resize_image(in_path, out_path)
        elif operation == 'enhance':
            out_path = os.path.join(UPLOAD_FOLDER, "enhanced_" + file.filename)
            image_tools.enhance_image(in_path, out_path)
        else: return "Unknown operation", 400
        return send_file(out_path, as_attachment=True)
    except Exception as e: return f"Error: {str(e)}", 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

if __name__ == '__main__':
    app.run(debug=True)
