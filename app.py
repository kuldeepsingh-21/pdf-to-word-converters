import os
from flask import Flask, request, send_file
# Adjusted imports to read directly from your main folder files
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
    <body class="bg-slate-900 text-slate-100 font-sans min-h-screen flex flex-col justify-between">
        <header class="bg-slate-950 border-b border-slate-800 py-4 px-6 flex justify-between items-center shadow-md">
            <a href="/" class="text-2xl font-black text-red-500 tracking-tight">Free PDF<span class="text-white"> Convert</span></a>
            <nav class="hidden md:flex space-x-6 text-sm font-medium text-slate-400">
                <a href="/" class="hover:text-red-500">Home</a>
                <a href="/about" class="hover:text-red-500">About Us</a>
                <a href="/contact" class="hover:text-red-500">Contact</a>
            </nav>
        </header>

        <main class="flex-grow max-w-4xl w-full mx-auto px-4 py-12 flex flex-col justify-center">
            {content}
        </main>

        <footer class="bg-slate-950 text-slate-500 text-center py-6 text-xs border-t border-slate-900">
            <div class="flex justify-center space-x-6 mb-3 text-sm">
                <a href="/about" class="hover:underline">About Us</a>
                <a href="/privacy" class="hover:underline">Privacy Policy</a>
                <a href="/terms" class="hover:underline">Terms & Conditions</a>
                <a href="/contact" class="hover:underline">Contact Us</a>
            </div>
            <p>&copy; 2026 Free PDF Convert. Processing running in sandbox memory units.</p>
        </footer>
    </body>
    </html>
    '''

@app.route('/')
def home():
    content = '''
    <div class="text-center mb-10">
        <h1 class="text-4xl font-extrabold text-white tracking-tight">Central Processing Station</h1>
        <p class="mt-2 text-slate-400">Select an algorithmic tool parameter from the drop-down to alter or convert files.</p>
    </div>

    <div class="bg-slate-950 p-8 rounded-2xl border border-slate-800 shadow-2xl max-w-xl w-full mx-auto">
        <form method="POST" action="/process-file" enctype="multipart/form-data" onsubmit="showLoading(this)">
            
            <div class="mb-6">
                <label class="block text-xs font-mono tracking-wider text-slate-400 mb-2 uppercase">Select Operation Type</label>
                <select name="operation" class="w-full bg-slate-900 border border-slate-700 rounded-xl px-4 py-3.5 text-sm text-white focus:outline-none focus:border-red-500 font-medium">
                    <option value="pdf2word">Convert: PDF to Word (.docx)</option>
                    <option value="img2pdf">Convert: Image (JPG/PNG) to PDF</option>
                    <option value="compress">Optimize: Compress PDF Size</option>
                    <option value="repair">System: Repair Corrupted PDF</option>
                    <option value="resize">Image: Resize & Compress File</option>
                    <option value="enhance">Image: Enhance Photo Matrix</option>
                </select>
            </div>

            <div class="mb-6">
                <label class="block text-xs font-mono tracking-wider text-slate-400 mb-2 uppercase">Upload Document Asset</label>
                <div class="border-2 border-dashed border-slate-700 hover:border-slate-500 rounded-xl p-6 bg-slate-900/50 text-center cursor-pointer relative">
                    <input type="file" name="file" required class="absolute inset-0 opacity-0 w-full h-full cursor-pointer" onchange="document.getElementById('file-name-display').textContent = 'Loaded: ' + this.files[0].name">
                    <p id="file-name-display" class="text-sm text-slate-400 font-medium">Click or Drag file parameters here</p>
                </div>
            </div>

            <button type="submit" class="w-full bg-gradient-to-r from-red-600 to-rose-700 hover:from-red-500 hover:to-rose-600 text-white font-bold py-3.5 px-6 rounded-xl transition shadow-lg shadow-red-950/30 text-sm tracking-wide uppercase">
                Execute Process Matrix
            </button>
        </form>
    </div>

    <script>
        function showLoading(form) {
            const btn = form.querySelector('button[type="submit"]');
            btn.disabled = true;
            btn.innerHTML = `RUNNING ALGORITHMS...`;
            btn.className = "w-full bg-slate-800 text-slate-500 font-bold py-3.5 px-6 rounded-xl cursor-not-allowed text-sm text-center animate-pulse";
        }
    </script>
    '''
    return render_layout("Universal Hub", content)

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
        elif operation == 'repair':
            out_path = os.path.join(UPLOAD_FOLDER, "repaired_" + file.filename)
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

@app.route('/about')
def page_about(): return render_layout("About Us", "<div class='bg-slate-950 p-8 rounded-xl border border-slate-800'><h1 class='text-2xl font-bold mb-4'>About Us</h1><p class='text-slate-400'>Free PDF Convert operates serverless sandbox engines to safely transform local data architectures.</p></div>")
@app.route('/privacy')
def page_privacy(): return render_layout("Privacy", "<div class='bg-slate-950 p-8 rounded-xl border border-slate-800'><h1 class='text-2xl font-bold mb-4'>Privacy</h1><p class='text-slate-400'>Data streams clean immediately on transaction close.</p></div>")
@app.route('/terms')
def page_terms(): return render_layout("Terms", "<div class='bg-slate-950 p-8 rounded-xl border border-slate-800'><h1 class='text-2xl font-bold mb-4'>Terms</h1><p class='text-slate-400'>Standard usage without liability models applies.</p></div>")
@app.route('/contact')
def page_contact(): return render_layout("Contact", "<div class='bg-slate-950 p-8 rounded-xl border border-slate-800'><h1 class='text-2xl font-bold mb-4'>Contact</h1><p class='text-slate-400'>Reach out at support@freepdfconvert.com</p></div>")

if __name__ == '__main__':
    app.run(debug=True)
