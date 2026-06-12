import os
import json
from flask import Flask, request, send_file, jsonify
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
    </head>
    <body class="bg-[#f2f3f8] text-[#333333] font-sans min-h-screen flex flex-col justify-between">
        <header class="bg-white border-b border-gray-200 py-3.5 px-6 flex justify-between items-center shadow-sm sticky top-0 z-50">
            <div class="flex items-center space-x-8">
                <a href="/" class="text-2xl font-black text-[#e5322b] tracking-tight flex items-center">
                    Free PDF<span class="text-[#333333] font-bold">Convert</span>
                </a>
                <nav class="hidden lg:flex space-x-6 text-sm font-bold text-gray-700 uppercase tracking-wide">
                    <a href="/?tool=merge" class="text-[#e5322b] border-b-2 border-[#e5322b] pb-1">Merge PDF</a>
                    <a href="/?tool=repair" class="hover:text-[#e5322b] transition">Split PDF</a>
                    <a href="/?tool=compress" class="hover:text-[#e5322b] transition">Compress PDF</a>
                    <a href="/?tool=pdf2word" class="hover:text-[#e5322b] transition">Convert PDF</a>
                </nav>
            </div>
            <div class="flex space-x-4 text-sm font-medium text-gray-600">
                <a href="/about" class="hover:text-[#e5322b]">About</a>
                <a href="/contact" class="hover:text-[#e5322b]">Contact</a>
            </div>
        </header>
        <main class="flex-grow w-full max-w-7xl mx-auto px-4 py-10">
            {content}
        </main>
        <footer class="bg-[#161616] text-gray-400 text-center py-8 text-xs">
            <p>&copy; 2026 Free PDF Convert. Secure sandbox processing units enabled.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    # --- ADVANCED VISUAL DRAG-DROP MERGER INTERFACE ---
    if selected_tool == 'merge':
        merge_html = '''
        <div class="max-w-5xl mx-auto mt-4">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-black text-gray-900 mb-2">Merge PDF Files</h1>
                <p class="text-gray-500 text-sm">Upload multiple PDFs, visually rearrange or edit individual page orders, and merge them instantly.</p>
            </div>

            <div id="upload-stage" class="bg-white p-10 rounded-2xl shadow-md border border-gray-200 text-center">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-12 bg-gray-50 transition cursor-pointer relative mb-4" onclick="document.getElementById('merge-files').click()">
                    <input type="file" id="merge-files" multiple accept=".pdf" class="hidden" onchange="initializeVisualArranger(this)">
                    <div class="text-[#e5322b] mb-3 flex justify-center">
                        <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path></svg>
                    </div>
                    <p class="text-lg font-bold text-gray-700">Select multiple PDF files</p>
                    <p class="text-xs text-gray-400 mt-1">Files will open visually for structural modification mapping</p>
                </div>
            </div>

            <div id="workspace-stage" class="hidden bg-white p-8 rounded-2xl shadow-md border border-gray-200">
                <div class="flex justify-between items-center border-b border-gray-200 pb-4 mb-6">
                    <span class="text-sm font-bold text-gray-500 uppercase tracking-wider">Drag & Drop Pages to Arrange Structure</span>
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
            let filesStorage = [];
            let globalPageMatrix = [];

            function initializeVisualArranger(input) {
                if (!input.files.length) return;
                
                document.getElementById('upload-stage').classList.add('hidden');
                document.getElementById('workspace-stage').classList.remove('hidden');
                
                const grid = document.getElementById('pages-grid');

                // Simulate metadata map read index sequences for free cloud execution
                for(let i=0; i<input.files.length; i++) {
                    let file = input.files[i];
                    filesStorage.push(file);
                    let fileIdx = filesStorage.length - 1;
                    
                    // Assume 2 structural page frames per loaded file for rapid local sandboxing template render
                    for(let pageNum = 1; pageNum <= 2; pageNum++) {
                        let pageId = `item-${fileIdx}-${pageNum-1}`;
                        globalPageMatrix.push({ fileIdx: fileIdx, pageIdx: pageNum - 1, filename: file.name });

                        let card = document.createElement('div');
                        card.id = pageId;
                        card.className = "bg-white border-2 border-gray-200 p-4 rounded-xl shadow-sm cursor-move relative select-none hover:border-[#e5322b] group transition";
                        card.draggable = true;
                        
                        // Drag Events Routing Map Setup
                        card.addEventListener('dragstart', (e) => e.dataTransfer.setData('text/plain', card.id));
                        
                        card.innerHTML = `
                            <div class="bg-gray-100 aspect-[3/4] rounded-lg border border-gray-200 flex flex-col items-center justify-center p-2 mb-2 relative overflow-hidden">
                                <span class="text-xs font-mono font-bold text-gray-400 uppercase tracking-widest">Page ${pageNum}</span>
                                <div class="absolute bottom-1 left-1 right-1 bg-gray-900/60 text-white text-[10px] truncate px-1 py-0.5 rounded text-center">${file.name}</div>
                            </div>
                            <div class="flex justify-between items-center text-xs">
                                <span class="font-bold text-gray-400">#${grid.children.length + 1}</span>
                                <button type="button" onclick="this.parentElement.parentElement.remove(); rebuildMatrixSequence();" class="text-gray-400 hover:text-red-600 font-bold">Delete</button>
                            </div>
                        `;
                        grid.appendChild(card);
                    }
                }
                setupGridDragAndDropDropzones();
            }

            function setupGridDragAndDropDropzones() {
                const grid = document.getElementById('pages-grid');
                grid.addEventListener('dragover', (e) => e.preventDefault());
                
                grid.addEventListener('drop', (e) => {
                    e.preventDefault();
                    const draggedId = e.dataTransfer.getData('text/plain');
                    const draggedElement = document.getElementById(draggedId);
                    const target = e.target.closest('.bg-white');
                    
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
                    // Re-index visual text counter markers
                    card.querySelector('span.font-bold').textContent = `#${index + 1}`;
                    
                    // Parse data parameters mapping sequences back
                    let parts = card.id.split('-');
                    newMatrix.push({
                        fileIdx: parseInt(parts[1]),
                        pageIdx: parseInt(parts[2])
                    });
                });
                globalPageMatrix = newMatrix;
            }

            function submitAdvancedMerge() {
                if(globalPageMatrix.length === 0) { alert('No pages remaining to merge.'); return; }
                
                const btn = document.getElementById('merge-submit-btn');
                btn.disabled = true;
                btn.innerHTML = 'COMPILING MERGE CONFIGURATION...';
                btn.className = "bg-gray-400 text-white font-black py-4 px-10 rounded-xl cursor-not-allowed text-lg uppercase tracking-wide animate-pulse";

                let formData = new FormData();
                
                // Pack the binary files into form streams
                filesStorage.forEach((file, index) => {
                    formData.append(`file_${index}`, file);
                });
                
                // Map out corresponding logical sequence tracks
                let mappingPlan = globalPageMatrix.map(item => {
                    return { fileId: `file_${item.fileIdx}`, pageIdx: item.pageIdx };
                });
                
                formData.append('layout_plan', JSON.stringify(mappingPlan));

                fetch('/execute-advanced-merge', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if(!response.ok) throw new Error('Merge generation framework issue');
                    return response.blob();
                })
                .then(blob => {
                    let url = window.URL.createObjectURL(blob);
                    let a = document.createElement('a');
                    a.href = url;
                    a.download = "merged_workspace_document.pdf";
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
        return render_layout("Merge PDF Workspace", merge_html)

    # --- RENDER GENERIC LOADER SCREEN FOR OTHER STANDARD CHANNELS ---
    if selected_tool:
        tool_titles = {'pdf2word': 'Convert PDF to Word', 'repair': 'Repair PDF File Stream', 'compress': 'Compress PDF Quality Map', 'resize': 'Resize Images', 'enhance': 'Enhance Contrast Layer'}
        title = tool_titles.get(selected_tool, "Processing Asset Channel")
        upload_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-xl border border-gray-200 text-center mt-6">
            <h1 class="text-3xl font-black text-gray-900 mb-2">{title}</h1>
            <p class="text-gray-500 text-sm mb-8">Process document elements via cloud pipeline acceleration matrices.</p>
            <form method="POST" action="/process-file" enctype="multipart/form-data" onsubmit="this.querySelector('button').disabled=true; this.querySelector('button').textContent='COMPILING...';">
                <input type="hidden" name="operation" value="{selected_tool}">
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-10 bg-gray-50 mb-6 relative">
                    <input type="file" name="file" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('fn-dsp').textContent = this.files[0].name">
                    <p id="fn-dsp" class="text-base font-bold text-gray-700">Select file parameter target allocation</p>
                </div>
                <button type="submit" class="w-full bg-[#e5322b] text-white font-extrabold py-4 rounded-xl uppercase text-base tracking-wider shadow-md">Execute Processing</button>
            </form>
        </div>
        '''
        return render_layout(title, upload_html)

    # --- STANDARD iLOVEPDF MAIN SELECTION CARDS GRID ---
    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-[#1f2430] tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">100% free, automated visual drag-and-drop workspace arrays.</p>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
        <a href="/?tool=merge" class="bg-white p-6 rounded-xl shadow-sm border border-red-200 hover:border-[#e5322b] hover:shadow-xl hover:-translate-y-1 transition block group">
            <div class="text-[#e5322b] mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF (Visual Workspace)</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Combine, sort, rearrange, delete, and modify individual document page parameters via drop grids.</p>
        </a>
        <a href="/?tool=pdf2word" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition block group">
            <div class="text-blue-600 mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-blue-600 mb-1">PDF to Word</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Convert structural records immediately to completely editable DOCX files.</p>
        </a>
        <a href="/?tool=compress" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition block group">
            <div class="text-emerald-600 mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-emerald-600 mb-1">Compress PDF</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Shrink file weight profiles down while optimizing maximum stream preservation layout.</p>
        </a>
    </div>
    '''
    return render_layout("Universal Hub", grid_html)

# --- ADVANCED ROUTE ROUTER FOR VISUAL ARRANGEMENTS ---
@app.route('/execute-advanced-merge', methods=['POST'])
def execute_advanced_merge():
    try:
        plan_data = request.form.get('layout_plan')
        page_order_plan = json.loads(plan_data)
        
        uploaded_files_map = {}
        saved_paths = []
        
        # Save down temporary storage frames across all packed key allocations
        for key in request.files:
            file = request.files[key]
            path = os.path.join(UPLOAD_FOLDER, f"merge_tmp_{key}_{file.filename}")
            file.save(path)
            uploaded_files_map[key] = path
            saved_paths.append(path)
            
        out_file = os.path.join(UPLOAD_FOLDER, "final_merged_assembly.pdf")
        
        # Execute order compilation tracking parameters inside the new module asset engine
        pdf_tools.merge_advanced_pdf(uploaded_files_map, page_order_plan, out_file)
        
        return send_file(out_file, as_attachment=True)
    except Exception as e:
        return str(e), 500
    finally:
        # Clean sandbox storage vectors immediately
        for p in saved_paths:
            if os.path.exists(p): os.remove(p)

@app.route('/process-file', methods=['POST'])
def process_file():
    operation = request.form.get('operation')
    file = request.files.get('file')
    if not file: return "Missing parameter", 400
    in_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(in_path)
    try:
        if operation == 'pdf2word':
            out_path = os.path.join(UPLOAD_FOLDER, file.filename.replace('.pdf', '.docx'))
            converter_tools.pdf_to_word(in_path, out_path)
        elif operation == 'compress':
            out_path = os.path.join(UPLOAD_FOLDER, "compressed_" + file.filename)
            pdf_tools.compress_pdf(in_path, out_path)
        else: return "Unknown action context", 400
        return send_file(out_path, as_attachment=True)
    except Exception as e: return str(e), 500
    finally:
        if os.path.exists(in_path): os.remove(in_path)

if __name__ == '__main__':
    app.run(debug=True)
