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
    <body class="bg-[#0f111a] text-[#e1e4ea] font-sans min-h-screen flex flex-col justify-between">
        
        <header class="bg-[#161925] border-b border-gray-800 py-3.5 px-6 flex justify-between items-center shadow-md sticky top-0 z-50">
            <div class="flex items-center space-x-8">
                <a href="/" class="text-2xl font-black text-[#ff3e3e] tracking-tight flex items-center">
                    Free PDF<span class="text-white font-bold ml-1">Convert</span>
                </a>
                <nav class="hidden lg:flex space-x-6 text-sm font-bold text-gray-400 uppercase tracking-wide">
                    <a href="/?tool=merge" class="text-[#ff3e3e] border-b-2 border-[#ff3e3e] pb-1">Merge PDF Workspace</a>
                    <a href="/?tool=pdf2word" class="hover:text-[#ff3e3e] transition">Convert PDF</a>
                    <a href="/?tool=compress" class="hover:text-[#ff3e3e] transition">Compress Size</a>
                </nav>
            </div>
            <div class="text-xs font-mono text-gray-500 bg-black/40 px-3 py-1.5 rounded-full border border-gray-800">
                CORE V3.0 • ENGINE ONLINE
            </div>
        </header>

        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-10">
            {content}
        </main>

        <footer class="bg-[#090a10] text-gray-600 text-center py-6 text-xs border-t border-gray-900">
            <p>&copy; 2026 Free PDF Convert Pro. Local execution parameters sandbox enforced.</p>
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
            <div class="text-center mb-10">
                <h1 class="text-4xl font-black text-white tracking-tight mb-2">High-Tech Merge & Page Organizer</h1>
                <p class="text-gray-400 text-sm max-w-xl mx-auto">Upload files directly from your desktop or pull them down from your Google Drive infrastructure to interactively arrange specific page sequences.</p>
            </div>

            <div id="upload-stage" class="bg-[#161925] p-12 rounded-2xl shadow-2xl border border-gray-800 text-center max-w-2xl mx-auto">
                <div class="border-2 border-dashed border-gray-700 hover:border-[#ff3e3e] rounded-xl p-12 bg-[#0f111a] transition cursor-pointer relative mb-6" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="loadPDFsToCanvasWorkspace(this.files)">
                    <div class="text-[#ff3e3e] mb-4 flex justify-center">
                        <svg class="w-16 h-16 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 13h6m-3-3v6m-9 1V7a2 2 0 012-2h6l2 2h6a2 2 0 012 2v8a2 2 0 01-2 2H5a2 2 0 01-2-2z"></path></svg>
                    </div>
                    <p class="text-xl font-bold text-gray-200">Select Multiple PDF Files From Desktop</p>
                    <p class="text-xs text-gray-500 mt-2">Supports multi-selection file parameters via native explorer</p>
                </div>

                <div class="relative flex py-2 items-center text-gray-600 text-xs font-mono uppercase tracking-widest my-4">
                    <div class="flex-grow border-t border-gray-800"></div>
                    <span class="mx-4">Cloud API Node Access</span>
                    <div class="flex-grow border-t border-gray-800"></div>
                </div>

                <button type="button" onclick="launchGoogleDrivePickerBridge()" class="w-full bg-gradient-to-r from-blue-600 to-emerald-600 hover:from-blue-500 hover:to-emerald-500 text-white font-bold py-3.5 px-6 rounded-xl transition shadow-lg flex items-center justify-center space-x-3 text-sm">
                    <svg class="w-5 h-5" viewBox="0 0 24 24" fill="currentColor"><path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM19 18H6c-2.21 0-4-1.79-4-4 0-2.05 1.53-3.76 3.56-3.97l1.07-.11.5-.95C8.08 7.14 9.94 6 12 6c2.62 0 4.88 1.86 5.39 4.43l.3 1.5 1.53.11c1.56.1 2.78 1.41 2.78 2.96 0 1.65-1.35 3-3 3z"/></svg>
                    <span>Import Documents via Google Drive</span>
                </button>
            </div>

            <div id="workspace-stage" class="hidden bg-[#161925] p-8 rounded-2xl shadow-2xl border border-gray-800">
                <div class="flex justify-between items-center border-b border-gray-800 pb-4 mb-6">
                    <span class="text-xs font-mono tracking-wider text-gray-400 uppercase">Live Pipeline Visualizer: Drag & Drop to Sort Page Frames</span>
                    <button onclick="document.getElementById('merge-files').click()" class="bg-gray-800 hover:bg-gray-700 text-gray-200 text-xs font-bold py-2 px-4 rounded-lg border border-gray-700 transition">+ Add Files</button>
                </div>

                <div id="pages-grid" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6 p-6 bg-[#0f111a] rounded-xl min-h-[250px] border border-gray-900"></div>

                <div class="mt-10 pt-6 border-t border-gray-800 flex justify-end">
                    <button onclick="submitAdvancedMerge()" id="merge-submit-btn" class="bg-gradient-to-r from-[#ff3e3e] to-red-700 hover:from-[#ff5555] hover:to-red-600 text-white font-black py-4 px-12 rounded-xl shadow-lg transition text-lg uppercase tracking-wide">
                        Compile & Download PDF
                    </button>
                </div>
            </div>
        </div>

        <script>
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';

            let filesStorage = [];
            let globalPageMatrix = [];

            // 1. Google Drive Integration Simulation Setup API Node
            function launchGoogleDrivePickerBridge() {
                alert("Google Drive API Access Layer Hook: To make cloud picker work natively in production environments, implement the Google Picker API inside your Google Developers Console dashboard, retrieve your ClientID token, and swap this alert action with a Google auth login framework window.");
            }

            // 2. High Tech Page Render Logic: Extracts actual previews out of document data packets
            async function loadPDFsToCanvasWorkspace(files) {
                if (!files.length) return;
                
                document.getElementById('upload-stage').classList.add('hidden');
                document.getElementById('workspace-stage').classList.remove('hidden');
                
                const grid = document.getElementById('pages-grid');

                for(let i=0; i<files.length; i++) {
                    let file = files[i];
                    filesStorage.push(file);
                    let fileIdx = filesStorage.length - 1;

                    // Convert standard file data structure streams into standard arrays readable by pdf.js
                    let fileReader = new FileReader();
                    fileReader.onload = async function() {
                        let typedarray = new Uint8Array(this.result);
                        let pdf = await pdfjsLib.getDocument(typedarray).promise;

                        // Loop through all genuine pages inside this file element container
                        for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                            let pageId = `item-${fileIdx}-${pageNum-1}`;
                            globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1 });

                            // Create UI card block structure elements
                            let card = document.createElement('div');
                            card.id = pageId;
                            card.className = "bg-[#1c1f2f] border border-gray-800 p-3 rounded-xl shadow-md cursor-move relative select-none hover:border-[#ff3e3e] group transition flex flex-col justify-between";
                            card.draggable = true;
                            
                            // Initialize standard element canvas targets to catch rendered bitmap frame imagery
                            let canvas = document.createElement('canvas');
                            canvas.className = "w-full rounded bg-black/40 border border-gray-900 shadow-inner mb-2 aspect-[3/4]";
                            
                            card.appendChild(canvas);

                            // Bottom meta text structure row blocks
                            let infoRow = document.createElement('div');
                            infoRow.className = "flex justify-between items-center text-xs mt-1 text-gray-400";
                            infoRow.innerHTML = `
                                <span class="font-mono text-gray-500 font-bold index-marker">#${grid.children.length + 1}</span>
                                <span class="text-[10px] truncate max-w-[80px] bg-black/30 px-1 py-0.5 rounded text-gray-500">${file.name}</span>
                                <button type="button" onclick="this.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-500 hover:text-red-500 font-bold font-mono">X</button>
                            `;
                            card.appendChild(infoRow);
                            grid.appendChild(card);

                            // Trigger rendering background tasks inside the client layout
                            renderPageThumbnailsToCanvas(pdf, pageNum, canvas);
                            card.addEventListener('dragstart', (e) => e.dataTransfer.setData('text/plain', card.id));
                        }
                        setupGridDragAndDropDropzones();
                    };
                    fileReader.readAsArrayBuffer(file);
                }
            }

            async function renderPageThumbnailsToCanvas(pdfInstance, pageNum, canvasElement) {
                let page = await pdfInstance.getPage(pageNum);
                let viewport = page.getViewport({ scale: 0.3 }); // Downscale viewport size calculation boundaries
                let context = canvasElement.getContext('2d');
                canvasElement.height = viewport.height;
                canvasElement.width = viewport.width;
                
                let renderContext = { canvasContext: context, viewport: viewport };
                page.render(renderContext);
            }

            function setupGridDragAndDropDropzones() {
                const grid = document.getElementById('pages-grid');
                grid.addEventListener('dragover', (e) => e.preventDefault());
                
                grid.addEventListener('drop', (e) => {
                    e.preventDefault();
                    const draggedId = e.dataTransfer.getData('text/plain');
                    const draggedElement = document.getElementById(draggedId);
                    const target = e.target.closest('.bg-white, .bg-\\\\[#1c1f2f\\\\]'); // Catch high tech dynamic utility class selectors safely
                    
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
                    card.querySelector('.index-marker').textContent = `#${index + 1}`;
                    let parts = card.id.split('-');
                    newMatrix.push({
                        fileIdx: parseInt(parts[1]),
                        pageIdx: parseInt(parts[2])
                    });
                });
                globalPageMatrix = newMatrix;
                if(globalPageMatrix.length === 0) { window.location.reload(); }
            }

            function submitAdvancedMerge() {
                if(globalPageMatrix.length === 0) return;
                
                const btn = document.getElementById('merge-submit-btn');
                btn.disabled = true;
                btn.innerHTML = 'SANDBOX RUNNING MATRIX ALGORITHMS...';
                btn.className = "bg-gray-800 text-gray-600 font-black py-4 px-12 rounded-xl cursor-not-allowed text-lg uppercase tracking-wide animate-pulse";

                let formData = new FormData();
                filesStorage.forEach((file, index) => {
                    formData.append(`file_${index}`, file);
                });
                
                let mappingPlan = globalPageMatrix.map(item => {
                    return { fileId: `file_${item.fileIdx}`, pageIdx: item.pageIdx };
                });
                
                formData.append('layout_plan', JSON.stringify(mappingPlan));

                fetch('/execute-advanced-merge', { method: 'POST', body: formData })
                .then(res => { if(!res.ok) throw new Error('Engine processing fault'); return res.blob(); })
                .then(blob => {
                    let url = window.URL.createObjectURL(blob);
                    let a = document.createElement('a');
                    a.href = url;
                    a.download = "organized_document_assembly.pdf";
                    document.body.appendChild(a);
                    a.click();
                    window.location.reload();
                })
                .catch(err => { alert(err.message); window.location.reload(); });
            }
        </script>
        '''
        return render_layout("Merge PDF Workspace", merge_html)

    # Fallback to standard app card dashboard panel layout views if merge tool parameter isn't chosen
    return render_layout("Universal Hub", "<div class='text-center py-20'><a href='/?tool=merge' class='bg-[#ff3e3e] px-8 py-4 font-bold rounded-xl text-white shadow-xl hover:bg-red-600 uppercase text-sm tracking-widest'>Enter Visual Merge Engine Workspace Suite &rarr;</a></div>")

@app.route('/execute-advanced-merge', methods=['POST'])
def execute_advanced_merge():
    try:
        plan_data = request.form.get('layout_plan')
        page_order_plan = json.loads(plan_data)
        uploaded_files_map = {}
        saved_paths = []
        
        for key in request.files:
            file = request.files[key]
            path = os.path.join(UPLOAD_FOLDER, f"merge_tmp_{key}_{file.filename}")
            file.save(path)
            uploaded_files_map[key] = path
            saved_paths.append(path)
            
        out_file = os.path.join(UPLOAD_FOLDER, "final_merged_assembly.pdf")
        pdf_tools.merge_advanced_pdf(uploaded_files_map, page_order_plan, out_file)
        return send_file(out_file, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        for p in saved_paths:
            if os.path.exists(p): os.remove(p)

if __name__ == '__main__':
    app.run(debug=True)
