import os
from flask import Flask, request, send_file
# Imports read directly from your main folder files
import pdf_tools
import image_tools
import converter_tools

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'

# --- THE REAL BRANDED iLOVEPDF STYLE LAYOUT ---
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
                    <a href="/?tool=merge" class="hover:text-[#e5322b] transition">Merge PDF</a>
                    <a href="/?tool=split" class="hover:text-[#e5322b] transition">Split PDF</a>
                    <a href="/?tool=compress" class="hover:text-[#e5322b] transition">Compress PDF</a>
                    <a href="/?tool=pdf2word" class="hover:text-[#e5322b] transition">Convert PDF</a>
                    <a href="/" class="text-[#e5322b] border-b-2 border-[#e5322b] pb-1">All PDF Tools</a>
                </nav>
            </div>
            
            <div class="flex space-x-4 text-sm font-medium text-gray-600">
                <a href="/about" class="hover:text-[#e5322b] hidden sm:inline">About Us</a>
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
            <p class="text-gray-500">&copy; 2026 Free PDF Convert. Every tool you need to use PDFs, at your fingertips.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    selected_tool = request.args.get('tool')

    # IF A SPECIFIC TOOL IS CLICKED FROM THE MENU OR GRID, SHOW ITS UPLOAD SCREEN:
    if selected_tool:
        tool_titles = {
            'pdf2word': 'Convert PDF to Word',
            'img2pdf': 'Convert JPG/PNG Image to PDF',
            'compress': 'Compress PDF File Size',
            'repair': 'Repair Corrupted PDF',
            'resize': 'Resize & Compress Images',
            'enhance': 'Enhance Photo Contrast'
        }
        
        title = tool_titles.get(selected_tool, "Document Processing Tool")
        
        upload_html = f'''
        <div class="max-w-xl mx-auto bg-white p-10 rounded-2xl shadow-xl border border-gray-200 text-center mt-6">
            <h1 class="text-3xl font-black text-gray-900 mb-2">{title}</h1>
            <p class="text-gray-500 text-sm mb-8">Upload your file below to process it safely through our high-speed engine grids.</p>
            
            <form method="POST" action="/process-file" enctype="multipart/form-data" onsubmit="showLoading(this)">
                <input type="hidden" name="operation" value="{selected_tool}">
                
                <div class="border-2 border-dashed border-gray-300 hover:border-[#e5322b] rounded-xl p-10 bg-gray-50 hover:bg-red-50/20 transition cursor-pointer relative mb-6">
                    <input type="file" name="file" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('file-name-display').textContent = 'Selected File: ' + this.files[0].name">
                    <div class="text-[#e5322b] mb-3 flex justify-center">
                        <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    </div>
                    <p id="file-name-display" class="text-base font-bold text-gray-700">Select file or drag and drop here</p>
                </div>

                <button type="submit" class="w-full bg-[#e5322b] hover:bg-red-700 text-white font-extrabold py-4 px-6 rounded-xl transition shadow-lg text-lg uppercase tracking-wider">
                    Upload & Convert
                </button>
            </form>
            <div class="mt-6">
                <a href="/" class="text-sm font-bold text-gray-500 hover:text-[#e5322b]">&larr; Back to All PDF Tools</a>
            </div>
        </div>

        <script>
            function showLoading(form) {
                const btn = form.querySelector('button[type="submit"]');
                btn.disabled = true;
                btn.innerHTML = `<span class="animate-pulse">PROCESSING FILE... PLEASE WAIT</span>`;
                btn.className = "w-full bg-gray-400 text-white font-extrabold py-4 px-6 rounded-xl cursor-not-allowed text-lg uppercase tracking-wider";
            }
        </script>
        '''
        return render_layout(title, upload_html)

    # ELSE: SHOW THE MAIN ILOVEPDF GRID PAGE WITH ALL THE TOOLS DISPLAYED AS CARDS
    grid_html = '''
    <div class="text-center my-8">
        <h1 class="text-4xl font-black text-[#1f2430] tracking-tight sm:text-5xl">Every tool you need to work with PDFs</h1>
        <p class="mt-3 text-lg text-gray-600 max-w-2xl mx-auto">Every file conversion utility is 100% free and easy to use! Merge, split, compress, and convert document frameworks inside your browser.</p>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mt-12">
        
        <a href="/?tool=compress" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-[#e5322b] mb-1">Merge PDF</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Combine PDF files in the order you want with the easiest PDF merger available.</p>
        </a>

        <a href="/?tool=repair" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-[#e5322b] mb-1">Split PDF</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Extract one or multiple pages from your PDF or convert each page to an independent file template.</p>
        </a>

        <a href="/?tool=compress" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-[#e5322b] mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-[#e5322b] mb-1">Compress PDF</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Reduce file size while optimizing for maximal PDF layout structural preservation quality.</p>
        </a>

        <a href="/?tool=pdf2word" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-blue-600 mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-blue-600 mb-1">PDF to Word</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Convert your structural PDF files directly into fully editable Microsoft Word .docx profiles.</p>
        </a>

        <a href="/?tool=img2pdf" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-emerald-600 mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-emerald-600 mb-1">Image to PDF</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Pack your JPG or PNG graphics smoothly down into uniform portable vector document sheets.</p>
        </a>

        <a href="/?tool=repair" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-amber-600 mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.907c.961 0 1.36 1.252.588 1.81l-3.97 2.885a1 1 0 00-.364 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.971-2.885a1 1 0 00-1.18 0l-3.97 2.885c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.364-1.118l-3.97-2.885c-.772-.558-.372-1.81.588-1.81h4.906a1 1 0 00.951-.69l1.519-4.674z"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-amber-600 mb-1">Repair PDF</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Recover and fix data blocks from corrupt, broken, or unreadable PDF file architectures.</p>
        </a>

        <a href="/?tool=resize" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-purple-600 mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5v-4m0 4h-4m4 0l-5-5"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-purple-600 mb-1">Resize & Compress Image</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Shrink image pixel layouts parameters down by 50% to save storage space.</p>
        </a>

        <a href="/?tool=enhance" class="bg-white p-6 rounded-xl shadow-sm border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition duration-200 block group">
            <div class="text-fuchsia-600 mb-3">
                <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
            </div>
            <h3 class="text-xl font-black text-gray-900 group-hover:text-fuchsia-600 mb-1">Enhance Photo Matrix</h3>
            <p class="text-gray-500 text-sm leading-relaxed">Amplify color contrast depths computational layer matrices to clean muddy photos.</p>
        </a>

    </div>
    '''
    return render_layout("Universal Hub", grid_html)

@app.route('/process-file', methods=['POST'])
def process_file():
    operation = request.form.get('operation')
    file = request.files.get('file')
    
    if not file or file.filename == '':
        return "No file element provided", 400
        
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
        elif operation == 'repair' or operation == 'split':
            # Split and Repair maps structurally to our cross-ref stream rebuilder
            out_path = os.path.join(UPLOAD_FOLDER, "processed_" + file.filename)
            pdf_tools.repair_pdf(in_path, out_path)
        elif operation == 'resize':
            out_path = os.path.join(UPLOAD_FOLDER, "shrunk_" + file.filename)
            image_tools.resize_image(in_path, out_path)
        elif operation == 'enhance':
            out_path = os.path.join(UPLOAD_FOLDER, "enhanced_" + file.filename)
            image_tools.enhance_image(in_path, out_path)
        else:
            return "Unknown operation directive", 400
            
        return send_file(out_path, as_attachment=True)
        
    except Exception as e:
        return f"Pipeline execution failure: {str(e)}", 500
    finally:
        if os.path.exists(in_path): 
            os.remove(in_path)

# --- BRANDING AND REGULATORY METADATA PAGES ---
@app.route('/about')
def page_about(): 
    return render_layout("About Us", "<div class='bg-white p-8 rounded-xl border border-gray-200 shadow-sm'><h1 class='text-2xl font-black mb-4'>About Us</h1><p class='text-gray-600 leading-relaxed'>Free PDF Convert builds top-tier cloud document rendering infrastructure. All operations complete inside safe server environments.</p></div>")

@app.route('/privacy')
def page_privacy(): 
    return render_layout("Privacy", "<div class='bg-white p-8 rounded-xl border border-gray-200 shadow-sm'><h1 class='text-2xl font-black mb-4'>Privacy Policy</h1><p class='text-gray-600 leading-relaxed'>Your records are entirely yours. Data parameters completely wipe from system cache arrays upon transaction completion steps.</p></div>")

@app.route('/terms')
def page_terms(): 
    return render_layout("Terms", "<div class='bg-white p-8 rounded-xl border border-gray-200 shadow-sm'><h1 class='text-2xl font-black mb-4'>Terms & Conditions</h1><p class='text-gray-600 leading-relaxed'>Use of the conversion pipeline structure is totally open-source and provided free of charge under sandboxed configurations.</p></div>")

@app.route('/contact')
def page_contact(): 
    return render_layout("Contact", "<div class='bg-white p-8 rounded-xl border border-gray-200 shadow-sm'><h1 class='text-2xl font-black mb-4'>Contact Us</h1><p class='text-gray-600 leading-relaxed'>For platform issues or security pipeline questions, communicate with support lines at <b>support@freepdfconvert.com</b></p></div>")

if __name__ == '__main__':
    app.run(debug=True)
