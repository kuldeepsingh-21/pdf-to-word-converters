import os
import json
from flask import Flask, request, send_file
import pdf_tools
import image_tools
import converter_tools

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'

SIZE_LIMIT_BYTES = 100 * 1024 * 1024

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
                    <a href="/?tool=split" class="hover:text-[#e5322b] transition">Split PDF Studio</a>
                    <a href="/?tool=compress" class="hover:text-[#e5322b] transition">Compress PDF</a>
                    <a href="/?tool=pdf2word" class="hover:text-[#e5322b] transition">Convert PDF</a>
                </nav>
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-8">
            {content}
        </main>

        <footer class="bg-[#161616] text-gray-400 text-center py-6 text-xs">
            <p>&copy; 2026 Free PDF Convert. Secure in-browser local privacy isolation units operational.</p>
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
                <p class="text-gray-500 text-sm">Combine multiple files with proportional content scaling matrices.</p>
            </div>
            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToSetupWorkspace(this.files, 'merge')">
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
        ''' + pdf_tools.merge_html_js_stubs() if hasattr(pdf_tools, 'merge_html_js_stubs') else ""
        return render_layout("Merge PDF", merge_html)

    # --- ADVANCED SPLIT & EXTRACT MASTER SUITE ---
    if selected_tool == 'split':
        split_html = '''
        <div class="max-w-6xl mx-auto">
            <div class="text-center mb-6">
                <h1 class="text-3xl font-black text-gray-900 mb-1">Split PDF Professional Workspace</h1>
                <p class="text-gray-500 text-sm">Supports visual card picking, chunk sorting, explicit ranges, and open-ended shortcut bounds.</p>
            </div>

            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-sm border border-gray-200 text-center max-w-xl mx-auto">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer" onclick="document.getElementById('split-file').click()">
                    <input type="file" id="split-file" accept=".pdf" class="hidden" onchange="loadPDFToSplitWorkspace(this.files[0])">
                    <p class="text-base font-bold text-gray-700">Select PDF File to Process</p>
                </div>
            </div>

            <div id="workspace-stage" class="hidden bg-white p-6 rounded-2xl shadow-md border border-gray-200">
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 bg-gray-50 p-6 rounded-xl border border-gray-200 mb-6">
                    <div class="flex flex-col">
                        <label class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">1. Splitting Mode Method</label>
                        <select id="split-mode-selector" onchange="toggleSplittingInputs(this.value)" class="bg-white border border-gray-300 rounded-lg p-2.5 text-xs font-bold text-gray-700 focus:outline-none focus:border-[#e5322b]">
                            <option value="visual">Visual Grid Picking (Select via clicks)</option>
                            <option value="burst">Burst Mode (Extract every single page separate)</option>
                            <option value="chunks">Split by Page Chunks (Fixed size pieces)</option>
                            <option value="range">Extract Range Input Fields (Custom values)</option>
                        </select>
                    </div>

                    <div id="parameter-input-box" class="flex flex-col hidden">
                        <label id="param-label" class="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">2. Enter Splitting Constraint</label>
                        <input type="text" id="split-parameter-field" placeholder="e.g. 5" class="bg-white border border-gray-300 rounded-lg p-2 text-xs font-bold focus:outline-none focus:border-[#e5322b]">
                        <p id="param-help-text" class="text-[10px] text-gray-400 mt-1 leading-tight"></p>
                    </div>

                    <div class="flex flex-col justify-end">
                        <button onclick="submitAdvancedSplittingModule()" id="split-submit-btn" class="w-full bg-[#e5322b] hover:bg-red-700 text-white font-black py-3 rounded-lg shadow transition text-xs uppercase tracking-wider">
                            Execute Split Processing
                        </button>
                    </div>
                </div>

                <div class="flex justify-between items-center border-b border-gray-200 pb-3 mb-4">
                    <span id="workspace-message-label" class="text-xs font-bold text-gray-400 uppercase tracking-wide">Click on cards below to mark them for extraction sequence</span>
                    <span id="page-count-display" class="text-xs font-mono font-bold bg-red-50 text-[#e5322b] px-2 py-1 rounded">0 Pages Loaded</span>
                </div>

                <div id="pages-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 p-4 bg-gray-50 rounded-xl min-h-[180px]"></div>
            </div>
        </div>

        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';
            let targetSplitFile = null;
            let visualSelectedIndices = new Set();
            let totalDocumentPages = 0;

            function toggleSplittingInputs(mode) {
                const paramBox = document.getElementById('parameter-input-box');
                const label = document.getElementById('param-label');
                const input = document.getElementById('split-parameter-field');
                const help = document.getElementById('param-help-text');
                const msgLabel = document.getElementById('workspace-message-label');

                paramBox.classList.add('hidden');
                msgLabel.textContent = "Click on cards below to mark them for extraction sequence";

                if(mode === "chunks") {
                    paramBox.classList.remove('hidden');
                    label.textContent = "Chunk Size (Pages per file)";
                    input.placeholder = "e.g. 3";
                    help.textContent = "Divides the document into smaller files containing this set number of pages.";
                    msgLabel.textContent = "Chunk Mode Active: File cards are displayed for reference order.";
                } else if(mode === "range") {
                    paramBox.classList.remove('hidden');
                    label.textContent = "Enter Page Ranges";
                    input.placeholder = "e.g. 1-3, 5, 8-";
                    help.textContent = "Supports commas, explicit hyphens, and open shortcuts like '4-' (page 4 to end).";
                    msgLabel.textContent = "Range Mode Active: Enter arguments inside input fields above.";
                } else if(mode === "burst") {
                    msgLabel.textContent = "Burst Mode Active: Every single page page splits out into separate items inside a ZIP folder container.";
                }
            }

            async function loadPDFToSplitWorkspace(file) {
                if (!file) return;
                if(file.size > 100 * 1024 * 1024) { alert("File exceeds local cloud sandbox resource limits (100MB limit)."); return; }
                targetSplitFile = file;

                document.getElementById('upload-stage').classList.add('hidden');
                document.getElementById('workspace-stage').classList.remove('hidden');
                const grid = document.getElementById('pages-grid');
                grid.innerHTML = "";

                let fileReader = new FileReader();
                fileReader.onload = async function() {
                    let typedarray = new Uint8Array(this.result);
                    let pdf = await pdfjsLib.getDocument(typedarray).promise;
                    totalDocumentPages = pdf.numPages;
                    document.getElementById('page-count-display').textContent = `${totalDocumentPages} Pages Loaded`;

                    for (let pageNum = 1; pageNum <= totalDocumentPages; pageNum++) {
                        let pageId = `page-node-${pageNum - 1}`;
                        let page = await pdf.getPage(pageNum);
                        let nativeViewport = page.getViewport({ scale: 1.0 });
                        let pageOrientation = (nativeViewport.width > nativeViewport.height) ? "landscape" : "portrait";

                        let card = document.createElement('div');
                        card.id = pageId;
                        card.className = "bg-white border-2 border-gray-200 p-3 rounded-xl shadow-sm cursor-pointer hover:border-gray-400 transition flex flex-col justify-between overflow-hidden gap-2 relative transition-all";
                        
                        let aspectClass = (pageOrientation === "landscape") ? "aspect-[4/3]" : "aspect-[3/4]";
                        let canvasBox = document.createElement('div');
                        canvasBox.className = `w-full ${aspectClass} overflow-hidden bg-white border border-gray-200 rounded flex items-center justify-center relative`;
                        
                        // Checkbox status overlay indicator
                        let checkOverlay = document.createElement('div');
                        checkOverlay.className = "absolute inset-0 bg-red-600/10 border-2 border-[#e5322b] hidden flex items-center justify-center text-white text-xs font-bold select-none z-10 rounded";
                        checkOverlay.innerHTML = '<span class="bg-[#e5322b] text-white px-2 py-1 rounded shadow-md uppercase tracking-wider font-sans text-[9px]">Selected</span>';
                        canvasBox.appendChild(checkOverlay);

                        let canvas = document.createElement('canvas');
                        canvas.className = "w-full h-full object-contain pointer-events-none";
                        canvasBox.appendChild(canvas);
                        card.appendChild(canvasBox);

                        let metaRow = document.createElement('div');
                        metaRow.className = "flex justify-between items-center text-xs text-gray-500 pt-1 font-sans";
                        metaRow.innerHTML = `<span class="font-bold index-lbl">#${pageNum}</span>`;
                        card.appendChild(metaRow);
                        grid.appendChild(card);

                        // Toggle item choice on card clicks
                        card.onclick = () => {
                            if(document.getElementById('split-mode-selector').value !== "visual") return;
                            let idx = pageNum - 1;
                            if(visualSelectedIndices.has(idx)) {
                                visualSelectedIndices.delete(idx);
                                checkOverlay.classList.add('hidden');
                                card.classList.remove('border-[#e5322b]');
                            } else {
                                visualSelectedIndices.add(idx);
                                checkOverlay.classList.remove('hidden');
                                card.classList.add('border-[#e5322b]');
                            }
                        };

                        let context = canvas.getContext('2d');
                        let thumbViewport = page.getViewport({ scale: 0.22 });
                        canvas.height = thumbViewport.height;
                        canvas.width = thumbViewport.width;
                        page.render({ canvasContext: context, viewport: thumbViewport });
                    }
                };
                fileReader.readAsArrayBuffer(file);
            }

            function submitAdvancedSplittingModule() {
                const mode = document.getElementById('split-mode-selector').value;
                const param = document.getElementById('split-parameter-field').value;
                const btn = document.getElementById('split-submit-btn');

                if(mode === "visual" && visualSelectedIndices.size === 0) {
                    alert("Please select at least 1 page thumbnail from the grid before continuing.");
                    return;
                }

                btn.disabled = true;
                btn.innerHTML = 'RUNNING SPLIT ENGINE...';
                btn.className = "w-full bg-gray-400 text-white font-black py-3 rounded-lg cursor-not-allowed text-xs uppercase animate-pulse";

                let formData = new FormData();
                formData.append("file", targetSplitFile);
                formData.append("mode", mode);
                formData.append("parameter_str", param);
                formData.append("selected_indices", JSON.stringify(Array.from(visualSelectedIndices)));

                fetch('/execute-advanced-split', { method: 'POST', body: formData })
                .then(res => {
                    if(!res.ok) return res.text().then(text => { throw new Error(text) });
                    
                    // Read the download header parameters to match exact filename outputs safely
                    const disposition = res.headers.get('Content-Disposition');
                    let name = "processed_document.pdf";
                    if(disposition && disposition.includes('zip')) { name = "extracted_split_archive.zip"; }
                    else if(disposition && disposition.includes('.zip')) { name = "extracted_split_archive.zip"; }
                    
                    return res.blob().then(blob => ({ blob, name }));
                })
                .then(({ blob, name }) => {
                    let url = window.URL.createObjectURL(blob);
                    let a = document.createElement('a');
                    a.href = url;
                    a.download = name;
                    document.body.appendChild(a);
                    a.click();
                    window.location.reload();
                })
                .catch(err => {
                    alert(err.message);
                    window.location.reload();
                });
            }
        </script>
        '''
        return render_layout("Split PDF Workspace", split_html)

    # --- SINGLE ITEM LOADER FALLBACK ---
    if selected_tool:
        tool_titles = {'compress': 'Compress PDF Engine', 'pdf2word': 'PDF to Word Converter'}
        title = tool_titles.get(selected_tool, "Converter Processing Module")
        upload_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-md border border-gray-200 text-center mt-6">
            <h1 class="text-2xl font-black text-gray-900 mb-2">{title}</h1>
            <form method="POST" action="/process-file" enctype="multipart/form-data" onsubmit="document.getElementById('sub-btn').disabled=true;">
                <input type="hidden" name="operation" value="{selected_tool}">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-10 bg-gray-50 mb-6 relative">
                    <input type="file" name="file" accept=".pdf" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('fn-dsp').textContent = this.files[0].name">
                    <p id="fn-dsp" class="text-base font-bold text-gray-700">Select file to proceed</p>
                </div>
                <button type="submit" id="sub-btn" class="w-full bg-[#e5322b] text-white font-extrabold py-4 rounded-xl uppercase">Process Data</button>
            </form>
        </div>
        '''
        return render_layout(title, upload_html)

    # --- MASTER CARDS HOME INDEX ---
    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-gray-900 tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">100% free online conversion suite with advanced workspace controls.</p>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mt-12">
        <a href="/?tool=merge" class="bg-white p-6 rounded-xl shadow-sm border border-gray-200 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF Workspace</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Combine multiple PDFs, manage canvas dimension parameters, and match fonts safely.</p>
        </a>
        <a href="/?tool=split" class="bg-white p-6 rounded-xl shadow-sm border border-red-200 hover:border-[#e5322b] hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3"><svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg></div>
            <h3 class="text-lg font-bold text-gray-900 group-hover:text-[#e5322b] mb-1">Split PDF Studio</h3>
            <p class="text-gray-500 text-xs leading-relaxed">Advanced burst, chunk sizes, custom ranges, and shortcuts into downloadable ZIP archives.</p>
        </a>
    </div>
    '''
    return render_layout("All PDF Tools", grid_html)

# --- BACKEND ENDPOINT FOR ALL SPLITTING METHOD STREAMS ---
@app.route('/execute-advanced-split', methods=['POST'])
def execute_advanced_split():
    file = request.files.get('file')
    mode = request.form.get('mode')
    parameter_str = request.form.get('parameter_str', '')
    indices_json = request.form.get('selected_indices', '[]')

    if not file: return "Missing input resource", 400

    in_path = os.path.join(UPLOAD_FOLDER, "split_master_" + file.filename)
    out_target = os.path.join(UPLOAD_FOLDER, "split_output_data")
    file.save(in_path)

    try:
        selected_indices = json.loads(indices_json)
        
        # Enforce file delivery rules: Multi-page splits output a ZIP, single ranges output a PDF
        is_zip = True
        if mode == "visual" or mode == "range":
            is_zip = False
        if mode == "burst" or mode == "chunks":
            is_zip = True

        out_filename = "archive.zip" if is_zip else "document.pdf"
        final_out_path = out_target + "_" + out_filename

        output_format = pdf_tools.split_pdf_advanced_core(
            in_path, mode, parameter_str, selected_indices, final_out_path, is_zip_request=is_zip
        )

        if output_format == "zip":
            return send_file(final_out_path, as_attachment=True, download_name="split_extracted_archive.zip")
        else:
            return send_file(final_out_path, as_attachment=True, download_name="extracted_pages_document.pdf")

    except Exception as e:
        return str(e), 400
    finally:
        if os.path.exists(in_path): os.remove(in_path)
        if 'final_out_path' in locals() and os.path.exists(final_out_path): os.remove(final_out_path)

if __name__ == '__main__':
    app.run(debug=True)
