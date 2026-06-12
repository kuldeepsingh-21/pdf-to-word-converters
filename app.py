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
                    <a href="/?tool=convert" class="hover:text-[#e5322b] transition">Convert Studio</a>
                </nav>
            </div>
        </header>
        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-8">
            {content}
        </main>
        <footer class="bg-[#161616] text-gray-400 text-center py-6 text-xs">
            <p>&copy; 2026 Free PDF Convert. Secure isolated environment enabled.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Merge PDF Workspace</h1>
                <p class="text-gray-500 text-sm">Maintains original layouts without cutting off content or overwriting fields.</p>
            </div>
            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToSetupWorkspace(this.files)">
                    <p class="text-base font-bold text-gray-700">Select Multiple PDF Files</p>
                </div>
            </div>
            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                <div class="flex flex-col md:flex-row justify-between items-center border-b border-gray-200 pb-4 mb-6 gap-4">
                    <div class="flex items-center gap-4">
                        <select id="global-size-setup" class="bg-gray-50 border border-gray-200 rounded-lg px-3 py-1.5 text-xs font-bold text-gray-700"><option value="original">Original Size</option><option value="A4">A4 Paper Canvas</option><option value="LETTER">US Letter Canvas</option></select>
                        <div class="bg-gray-100 p-1 rounded-lg flex items-center border text-xs font-mono h-8">
                            <button onclick="adjustWorkspaceZoom(-10)" class="px-2 font-black">-</button>
                            <span id="zoom-value" class="px-2 font-bold">100%</span>
                            <button onclick="adjustWorkspaceZoom(10)" class="px-2 font-black">+</button>
                        </div>
                    </div>
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-100 text-gray-700 text-xs font-bold py-2 px-4 rounded-lg border border-gray-300 transition">+ Add Files</button>
                </div>
                <div id="pages-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[200px]"></div>
                <div class="mt-8 pt-4 border-t border-gray-200 flex justify-end">
                    <button onclick="submitPageSetupMerge()" id="merge-submit-btn" class="bg-[#e5322b] hover:bg-red-700 text-white font-black py-4 px-12 rounded-xl shadow-lg text-md uppercase">Compile & Merge PDF</button>
                </div>
            </div>
        </div>
        ''' + self_contained_javascript_logic()
        return render_layout("Merge PDF", merge_html)

    if selected_tool == 'split':
        split_html = '''
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Split PDF Studio</h1>
                <p class="text-gray-500 text-sm">Extract ranges, page chunks, or burst pages into a compressed ZIP file.</p>
            </div>
            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('split-file').click()">
                    <input type="file" id="split-file" accept=".pdf" class="hidden" onchange="loadPDFToSplitWorkspace(this.files[0])">
                    <p class="text-base font-bold text-gray-700">Select PDF File to Split</p>
                </div>
            </div>
            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 bg-gray-50 p-4 rounded-xl border mb-6 text-xs">
                    <div class="flex flex-col">
                        <label class="font-bold mb-1 uppercase text-gray-400">Splitting Mode</label>
                        <select id="split-mode-selector" onchange="toggleSplittingInputs(this.value)" class="bg-white border rounded p-2 font-bold">
                            <option value="visual">Visual Grid Selection (Click cards)</option>
                            <option value="burst">Burst Mode (Extract every single page separate)</option>
                            <option value="chunks">Split by Chunks (Fixed size pieces)</option>
                            <option value="range">Extract Custom Range (e.g. 1-4, 7-)</option>
                        </select>
                    </div>
                    <div id="parameter-input-box" class="flex flex-col hidden">
                        <label class="font-bold mb-1 uppercase text-gray-400">Parameters / Ranges</label>
                        <input type="text" id="split-parameter-field" placeholder="e.g. 3" class="bg-white border rounded p-2 font-bold">
                    </div>
                    <div class="flex flex-col justify-end">
                        <button onclick="submitAdvancedSplittingModule()" id="split-submit-btn" class="bg-[#e5322b] text-white font-bold py-3 rounded-lg uppercase shadow">Run Split Engine</button>
                    </div>
                </div>
                <div class="flex justify-between items-center text-xs font-bold text-gray-400 border-b pb-2 mb-4">
                    <span>Selected file configuration page breakdown mapping</span>
                    <span id="page-count-display" class="bg-red-50 text-[#e5322b] px-2 py-1 rounded">0 Pages</span>
                </div>
                <div id="pages-grid" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[180px]"></div>
            </div>
        </div>
        ''' + self_contained_javascript_logic()
        return render_layout("Split PDF Studio", split_html)

    if selected_tool == 'compress':
        compress_html = '''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-md border border-gray-200 mt-6">
            <h1 class="text-2xl font-black text-gray-900 mb-2 text-center">Compress PDF Engine</h1>
            <form method="POST" action="/execute-compression" enctype="multipart/form-data">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-8 bg-gray-50 mb-6 text-center relative cursor-pointer">
                    <input type="file" name="file" accept=".pdf" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('fn-dsp').textContent = 'Selected: ' + this.files[0].name">
                    <p id="fn-dsp" class="text-sm font-bold text-gray-700">Select PDF document to compress</p>
                </div>
                <div class="mb-6 text-xs flex flex-col">
                    <label class="font-bold text-gray-400 mb-1 uppercase">Compression Level</label>
                    <select name="level" class="bg-gray-50 border p-2.5 rounded-lg font-bold text-gray-700">
                        <option value="basic">Basic Compression (150 DPI - Quality Preservation)</option>
                        <option value="strong">Strong Compression (72 DPI - Maximum Size Reduction)</option>
                    </select>
                </div>
                <button type="submit" class="w-full bg-[#e5322b] text-white font-extrabold py-3.5 rounded-xl shadow uppercase text-sm">Optimize Size</button>
            </form>
        </div>
        '''
        return render_layout("Compress PDF", compress_html)

    if selected_tool == 'convert':
        convert_html = '''
        <div class="max-w-5xl mx-auto mt-4">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Universal Convert Studio</h1>
                <p class="text-gray-500 text-sm">Two-way formatting pipelines supporting structural webpage captures.</p>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <h3 class="text-base font-bold mb-4 border-b pb-2 text-gray-800">File Conversions</h3>
                    <form method="POST" action="/execute-studio-conversion" enctype="multipart/form-data" class="text-xs font-medium space-y-4">
                        <div><label class="block font-bold text-gray-400 mb-1 uppercase">Select File</label><input type="file" name="file" required class="w-full bg-gray-50 p-2 border rounded"></div>
                        <div><label class="block font-bold text-gray-400 mb-1 uppercase">Target Format</label>
                            <select name="operation" class="w-full bg-gray-50 border p-2 rounded font-bold text-gray-700">
                                <option value="pdf2word">Convert PDF to Editable Word (.docx)</option>
                                <option value="img2pdf_p">Convert Image to PDF (Forced Portrait Layout)</option>
                                <option value="img2pdf_l">Convert Image to PDF (Forced Landscape Layout)</option>
                                <option value="extract_img">Extract Embedded Raw Images from PDF</option>
                            </select>
                        </div>
                        <button type="submit" class="w-full bg-[#e5322b] text-white font-bold py-2.5 rounded-xl uppercase shadow">Convert Asset</button>
                    </form>
                </div>
                <div class="bg-white p-6 rounded-2xl shadow-sm border border-gray-200">
                    <h3 class="text-base font-bold mb-4 border-b pb-2 text-gray-800">Web Capture (HTML to PDF)</h3>
                    <form method="POST" action="/execute-web-capture" class="text-xs font-medium space-y-4">
                        <div><label class="block font-bold text-gray-400 mb-1 uppercase">Paste Source HTML Content</label><textarea name="html_text" rows="4" required class="w-full bg-gray-50 border p-2 rounded font-mono focus:outline-none"></textarea></div>
                        <div class="flex items-center space-x-2"><input type="checkbox" name="pdf_a" id="pdf_a" class="text-[#e5322b]"><label for="pdf_a" class="text-gray-500 font-medium">Preserve PDF/A long-term archiving standard</label></div>
                        <button type="submit" class="w-full bg-blue-600 text-white font-bold py-2.5 rounded-xl uppercase shadow">Capture Page Stream</button>
                    </form>
                </div>
            </div>
        </div>
        '''
        return render_layout("Convert Studio", convert_html)

    if request.args.get('orig_size'):
        o, c = int(request.args.get('orig_size')), int(request.args.get('comp_size'))
        savings = round(((o - c) / o) * 100, 1)
        success_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-md border text-center mt-6">
            <h2 class="text-2xl font-black text-gray-900 mb-2">Compression Complete!</h2>
            <div class="grid grid-cols-3 gap-4 bg-gray-50 p-4 rounded-xl border text-xs font-mono mb-6">
                <div><p class="text-gray-400 uppercase font-sans font-bold">Before</p><p class="font-bold mt-1">{(o/1024):.1f} KB</p></div>
                <div><p class="text-gray-400 uppercase font-sans font-bold">After</p><p class="text-green-600 font-bold mt-1">{(c/1024):.1f} KB</p></div>
                <div><p class="text-gray-400 uppercase font-sans font-bold">Reduced</p><p class="text-blue-600 font-bold mt-1">-{savings}%</p></div>
            </div>
            <a href="/retrieve-file?file={request.args.get('filename')}" class="block w-full bg-green-600 text-white font-extrabold py-3.5 rounded-xl shadow uppercase text-sm">Download Compressed PDF</a>
        </div>
        '''
        return render_layout("Size Metrics Report", success_html)

    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-gray-900 tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">100% free online conversion suite with advanced workspace controls.</p>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-12">
        <a href="/?tool=merge" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF Workspace</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Combine multiple PDFs, manage canvas size variables, and lock form field alignments safely.</p>
        </a>
        <a href="/?tool=split" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Split PDF Studio</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Advanced burst, chunk sizes, custom ranges, and shortcuts into downloadable ZIP archives.</p>
        </a>
        <a href="/?tool=compress" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Compress PDF Suite</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Advanced stream-content quantization reduction to scale file weights down safely.</p>
        </a>
        <a href="/?tool=convert" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Convert PDF Studio</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Two-way transitions, pull embedded raw graphic elements, or run secure web capture HTML streams.</p>
        </a>
    </div>
    '''
    return render_layout("All PDF Tools", grid_html)

def self_contained_javascript_logic():
    return '''
    <div id="inspector-modal" class="hidden fixed inset-0 bg-black/80 z-50 backdrop-blur-sm flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl w-full max-w-4xl h-[85vh] flex flex-col justify-between shadow-2xl relative">
            <div class="p-4 border-b flex justify-between items-center bg-gray-50 rounded-t-2xl">
                <h3 id="inspector-title" class="text-sm font-bold text-gray-700 truncate">Document Full Size Viewport</h3>
                <button onclick="document.getElementById('inspector-modal').classList.add('hidden')" class="bg-gray-200 hover:bg-red-600 hover:text-white text-gray-700 font-black px-3 py-1.5 rounded-lg text-xs">✕ Close Full Size</button>
            </div>
            <div class="flex-grow p-4 overflow-auto bg-gray-100 flex items-center justify-center"><canvas id="inspector-canvas" class="max-w-full max-h-full shadow-md rounded bg-white object-contain"></canvas></div>
        </div>
    </div>
    <script>
        let filesStorage = []; let globalPageMatrix = []; let currentZoom = 100; let loadedDocsMap = {};
        function adjustWorkspaceZoom(val) {
            currentZoom = Math.max(60, Math.min(150, currentZoom + val)); document.getElementById('zoom-value').textContent = currentZoom + '%';
            document.querySelectorAll('.canvas-viewport-box').forEach(box => { box.style.transform = `scale(${currentZoom / 100})`; });
        }
        function openInspectorModal(fileKey, pageNum) {
            const modal = document.getElementById('inspector-modal'); const canvas = document.getElementById('inspector-canvas'); modal.classList.remove('hidden');
            document.getElementById('inspector-title').textContent = `Full Page Inspector - Page ${pageNum}`;
            let pdfDoc = loadedDocsMap[fileKey]; if (pdfDoc) {
                pdfDoc.getPage(pageNum).then(page => {
                    let ctx = canvas.getContext('2d'); let viewport = page.getViewport({ scale: 1.4 }); canvas.height = viewport.height; canvas.width = viewport.width; page.render({ canvasContext: ctx, viewport: viewport });
                });
            }
        }
        function toggleCardLayoutSetup(cardId, val) {
            const targetCard = document.getElementById(cardId); targetCard.setAttribute('data-layout', val);
            const canvasBox = targetCard.querySelector('.canvas-viewport-box');
            canvasBox.className = `canvas-viewport-box w-full overflow-hidden bg-white border border-gray-300 rounded shadow-sm flex items-center justify-center origin-center transition-all ${val === "landscape" ? "aspect-[4/3]" : "aspect-[3/4]"}`;
            rebuildMatrixSequence();
        }
        function toggleSplittingInputs(mode) {
            const paramBox = document.getElementById('parameter-input-box');
            if(mode === "chunks" || mode === "range") paramBox.classList.remove('hidden'); else paramBox.classList.add('hidden');
        }
        async function loadPDFsToSetupWorkspace(files) {
            if (!files.length) return; document.getElementById('upload-stage').classList.add('hidden'); document.getElementById('workspace-stage').classList.remove('hidden');
            const grid = document.getElementById('pages-grid');
            for(let i=0; i<files.length; i++) {
                let file = files[i]; if(file.size > 100*1024*1024) { alert("File exceeds 100MB limit constraint."); return; }
                filesStorage.push(file); let fileIdx = filesStorage.length - 1; let fileKey = "file_" + fileIdx;
                let fileReader = new FileReader(); fileReader.readAsArrayBuffer(file);
                fileReader.onload = async function() {
                    let typedarray = new Uint8Array(this.result); let pdf = await pdfjsLib.getDocument(typedarray).promise; loadedDocsMap[fileKey] = pdf;
                    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                        let pageId = "item-" + fileIdx + "-" + (pageNum - 1); let page = await pdf.getPage(pageNum); let nativeViewport = page.getViewport({ scale: 1.0 });
                        let initialLayout = (nativeViewport.width > nativeViewport.height) ? "landscape" : "portrait";
                        globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1, layout: initialLayout });
                        let card = document.createElement('div'); card.id = pageId; card.setAttribute('data-layout', initialLayout);
                        card.className = "bg-white border p-3 rounded-xl shadow-sm cursor-move relative flex flex-col justify-between overflow-hidden gap-3 group"; card.draggable = true;
                        let aspectClass = (initialLayout === "landscape") ? "aspect-[4/3]" : "aspect-[3/4]";
                        let canvasBox = document.createElement('div'); canvasBox.className = `canvas-viewport-box w-full ${aspectClass} overflow-hidden bg-white border rounded shadow-inner flex items-center justify-center origin-center transition-all relative`;
                        let overlayBtn = document.createElement('button'); overlayBtn.className = "absolute inset-0 bg-black/40 text-white font-bold opacity-0 group-hover:opacity-100 flex items-center justify-center text-xs transition z-10";
                        overlayBtn.innerHTML = "🔍 View Full Page"; overlayBtn.onclick = (e) => { e.stopPropagation(); openInspectorModal(fileKey, pageNum); }; canvasBox.appendChild(overlayBtn);
                        let canvas = document.createElement('canvas'); canvas.className = "w-full h-full object-contain pointer-events-none"; canvasBox.appendChild(canvas); card.appendChild(canvasBox);
                        let controlRow = document.createElement('div'); controlRow.className = "flex flex-col gap-1 text-xs border-t pt-2 z-20 relative";
                        controlRow.innerHTML = `<div class="flex justify-between items-center text-gray-500"><span class="font-bold index-lbl">#${grid.children.length + 1}</span><span class="truncate max-w-[80px] text-[10px] bg-gray-100 px-1 rounded">${file.name}</span><button type="button" onclick="this.parentElement.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">X</button></div>
                        <div class="flex items-center justify-between gap-1"><label class="text-[9px] text-gray-400 font-mono">Page Setup:</label><select onchange="toggleCardLayoutSetup('${pageId}', this.value)" class="bg-gray-50 border rounded text-[11px] font-bold text-gray-700"><option value="portrait" ${initialLayout==="portrait"?"selected":""}>Portrait</option><option value="landscape" ${initialLayout==="landscape"?"selected":""}>Landscape</option></select></div>`;
                        card.appendChild(controlRow); grid.appendChild(card);
                        let context = canvas.getContext('2d'); let thumbViewport = page.getViewport({ scale: 0.25 }); canvas.height = thumbViewport.height; canvas.width = thumbViewport.width; page.render({ canvasContext: context, viewport: thumbViewport });
                        card.addEventListener('dragstart', (e) => e.dataTransfer.setData('text/plain', card.id));
                    }
                    setupDragAndDrop(); adjustWorkspaceZoom(0);
                };
            }
        }
        async function loadPDFToSplitWorkspace(file) {
            if (!file) return; if(file.size > 100*1024*1024) { alert("File exceeds 100MB limit."); return; }
            targetSplitFile = file; document.getElementById('upload-stage').classList.add('hidden'); document.getElementById('workspace-stage').classList.remove('hidden');
            const grid = document.getElementById('pages-grid'); grid.innerHTML = "";
            let fileReader = new FileReader(); fileReader.readAsArrayBuffer(file);
            fileReader.onload = async function() {
                let typedarray = new Uint8Array(this.result); let pdf = await pdfjsLib.getDocument(typedarray).promise; loadedDocsMap["file_0"] = pdf;
                document.getElementById('page-count-display').textContent = `${pdf.numPages} Pages Loaded`;
                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                    let pageId = `page-node-${pageNum - 1}`; let page = await pdf.getPage(pageNum); let nativeViewport = page.getViewport({ scale: 1.0 });
                    let pageOrientation = (nativeViewport.width > nativeViewport.height) ? "landscape" : "portrait"; globalPageMatrix.push({ pageIdx: pageNum - 1 });
                    let card = document.createElement('div'); card.id = pageId; card.className = "bg-white border p-3 rounded-xl shadow-sm cursor-pointer hover:border-gray-400 transition flex flex-col justify-between overflow-hidden gap-2 group relative";
                    let aspectClass = (pageOrientation === "landscape") ? "aspect-[4/3]" : "aspect-[3/4]";
                    let canvasBox = document.createElement('div'); canvasBox.className = `canvas-viewport-box w-full ${aspectClass} overflow-hidden bg-white border rounded flex items-center justify-center relative`;
                    let overlayBtn = document.createElement('button'); overlayBtn.className = "absolute inset-0 bg-black/40 text-white font-bold opacity-0 group-hover:opacity-100 flex items-center justify-center text-xs transition rounded z-10";
                    overlayBtn.innerHTML = "🔍 View Full Page"; overlayBtn.onclick = (e) => { e.stopPropagation(); openInspectorModal("file_0", pageNum); }; canvasBox.appendChild(overlayBtn);
                    let canvas = document.createElement('canvas'); canvas.className = "w-full h-full object-contain pointer-events-none"; canvasBox.appendChild(canvas); card.appendChild(canvasBox);
                    let metaRow = document.createElement('div'); metaRow.className = "flex justify-between items-center text-xs text-gray-500 pt-1 border-t border-gray-100 z-20 relative";
                    metaRow.innerHTML = `<span class="font-bold index-lbl">#${grid.children.length + 1}</span><button type="button" onclick="this.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">X</button>`;
                    card.appendChild(metaRow); grid.appendChild(card);
                    let context = canvas.getContext('2d'); let thumbViewport = page.getViewport({ scale: 0.22 }); canvas.height = thumbViewport.height; canvas.width = thumbViewport.width; page.render({ canvasContext: context, viewport: thumbViewport });
                }
                document.getElementById('split-mode-selector').value = "visual";
            }
        }
        function setupDragAndDrop() {
            const grid = document.getElementById('pages-grid'); grid.addEventListener('dragover', (e) => e.preventDefault());
            grid.addEventListener('drop', (e) => {
                e.preventDefault(); const draggedId = e.dataTransfer.getData('text/plain'); const draggedElement = document.getElementById(draggedId); const target = e.target.closest('#pages-grid > div');
                if (draggedElement && target && draggedElement !== target) {
                    const children = Array.from(grid.children); const draggedPos = children.indexOf(draggedElement); const targetPos = children.indexOf(target);
                    if (draggedPos < targetPos) grid.insertBefore(draggedElement, target.nextSibling); else grid.insertBefore(draggedElement, target);
                    rebuildMatrixSequence();
                }
            });
        }
        function rebuildMatrixSequence() {
            const grid = document.getElementById('pages-grid'); let newMatrix = [];
            Array.from(grid.children).forEach((card, index) => {
                card.querySelector('.index-lbl').textContent = '#' + (index + 1); let parts = card.id.split('-');
                if(parts[0] === "item") newMatrix.push({ fileIdx: parseInt(parts[1]), pageIdx: parseInt(parts[2]), layout: card.getAttribute('data-layout') || 'portrait' });
                else newMatrix.push({ pageIdx: parseInt(parts[2]) });
            });
            globalPageMatrix = newMatrix;
        }
        function submitPageSetupMerge() {
            if(globalPageMatrix.length === 0) return; const btn = document.getElementById('merge-submit-btn'); btn.disabled = true; btn.innerHTML = 'PROCESSING CHANNELS...';
            let formData = new FormData(); filesStorage.forEach((file, index) => { formData.append("file_" + index, file); });
            formData.append('global_size_setup', document.getElementById('global-size-setup').value);
            formData.append('layout_plan', JSON.stringify(globalPageMatrix.map(item => ({ fileId: "file_" + item.fileIdx, pageIdx: item.pageIdx, layout: item.layout }))));
            fetch('/execute-advanced-merge', { method: 'POST', body: formData }).then(res => res.blob()).then(blob => {
                let url = window.URL.createObjectURL(blob); let a = document.createElement('a'); a.href = url; a.download = "merged_document.pdf"; a.click(); window.location.reload();
            });
        }
        function submitAdvancedSplittingModule() {
            const mode = document.getElementById('split-mode-selector').value; const param = document.getElementById('split-parameter-field').value;
            let formData = new FormData(); formData.append("file", targetSplitFile); formData.append("mode", mode); formData.append("parameter_str", param); formData.append("selected_indices", JSON.stringify(globalPageMatrix.map(item => item.pageIdx)));
            fetch('/execute-advanced-split', { method: 'POST', body: formData }).then(res => res.blob()).then(blob => {
                let url = window.URL.createObjectURL(blob); let a = document.createElement('a'); a.href = url; a.download = mode === "burst" || mode === "chunks" ? "archive.zip" : "extracted.pdf"; a.click(); window.location.reload();
            });
        }
    </script>
    '''

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
    except Exception as e: return str(e), 400
    finally:
        for p in saved_paths:
            if os.path.exists(p): os.remove(p)

@app.route('/execute-advanced-split', methods=['POST'])
def execute_advanced_split():
    file = request.files.get('file')
    mode = request.form.get('mode')
    parameter_str = request.form.get('parameter_str', '')
    indices_json = request.form.get('selected_indices', '[]')
    if not file: return "Missing File", 400
    in_path = os.path.join(UPLOAD_FOLDER, "split_master_" + file.filename)
    final_out_path = os.path.join(UPLOAD_FOLDER, "split_out_" + file.filename + (".zip" if mode in ["burst", "chunks"] else ".pdf"))
    file.save(in_path)
    try:
        selected_indices = json.loads(indices_json)
        is_zip = True if mode in ["burst", "chunks"] else False
        pdf_tools.split_pdf_advanced_core(in_path, mode, parameter_str, selected_indices, final_out_path, is_zip_request=is_zip)
        return send_file(final_out_path, as_attachment=True)
    except Exception as e: return str(e), 400
    finally:
        if os.path.exists(in_path): os.remove(in_path)
        if os.path.exists(final_out_path): os.remove(final_out_path)

@app.route('/execute-compression', methods=['POST'])
def execute_compression():
    file = request.files.get('file')
    level = request.form.get('level', 'basic')
    if not file: return "Missing file", 400
    in_path = os.path.join(UPLOAD_FOLDER, "c_in_" + file.filename)
    out_path = os.path.join(UPLOAD_FOLDER, "c_out_" + file.filename)
    file.save(in_path)
    try:
        orig_size = os.path.getsize(in_path)
        pdf_tools.advanced_compress_quantization_engine(in_path, level, out_path)
        comp_size = os.path.getsize(out_path)
        return f'''<script>window.location.href="/?orig_size={orig_size}&comp_size={comp_size}&filename={file.filename}";</script>'''
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

@app.route('/retrieve-file')
def retrieve_file():
    filename = request.args.get('file', '')
    path = os.path.join(UPLOAD_FOLDER, "c_out_" + filename)
    if os.path.exists(path): return send_file(path, as_attachment=True, download_name="optimized_" + filename)
    return "File lost from temp memory buffers.", 404

@app.route('/execute-studio-conversion', methods=['POST'])
def execute_studio_conversion():
    file = request.files.get('file')
    operation = request.form.get('operation')
    if not file: return "Missing file", 400
    in_path = os.path.join(UPLOAD_FOLDER, "conv_" + file.filename)
    file.save(in_path)
    try:
        if operation == 'pdf2word':
            out_path = os.path.join(UPLOAD_FOLDER, file.filename.replace('.pdf', '.docx'))
            converter_tools.pdf_to_word(in_path, out_path)
            return send_file(out_path, as_attachment=True, download_name="converted_document.docx")
        elif operation in ['img2pdf_p', 'img2pdf_l']:
            out_path = os.path.join(UPLOAD_FOLDER, "img_out_" + file.filename + ".pdf")
            ort = "portrait" if operation == 'img2pdf_p' else "landscape"
            converter_tools.img_to_pdf_adjusted(in_path, out_path, orientation=ort, margins="standard")
            return send_file(out_path, as_attachment=True, download_name="image_converted.pdf")
        elif operation == 'extract_img':
            out_zip = os.path.join(UPLOAD_FOLDER, "extracted_assets.zip")
            extracted_paths = converter_tools.extract_images_from_pdf(in_path, UPLOAD_FOLDER)
            if not extracted_paths: return "No image objects detected.", 400
            with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as z:
                for p in extracted_paths:
                    z.write(p, os.path.basename(p))
                    if os.path.exists(p): os.remove(p)
            return send_file(out_zip, as_attachment=True, download_name="extracted_pdf_images.zip")
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

@app.route('/execute-web-capture', methods=['POST'])
def execute_web_capture():
    html_markup = request.form.get('html_text', '')
    pdf_a_checked = True if request.form.get('pdf_a') else False
    if not html_markup: return "Content parameter empty", 400
    out_pdf = os.path.join(UPLOAD_FOLDER, "web_capture_output.pdf")
    try:
        converter_tools.html_web_capture_to_pdf(html_markup, out_pdf, convert_to_pdf_a=pdf_a_checked)
        return send_file(out_pdf, as_attachment=True, download_name="captured_webpage.pdf")
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(out_pdf): os.remove(out_pdf)

if __name__ == '__main__':
    app.run(debug=True)
