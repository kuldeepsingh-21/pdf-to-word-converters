@app.route('/')
def index():
    return '''
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Convert PDF to WORD Online - Free</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-50 font-sans min-h-screen flex flex-col justify-between">

        <header class="bg-white shadow-sm border-b border-gray-200 py-4 px-6 flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <span class="text-2xl font-black text-red-600 tracking-tight">iLove<span class="text-gray-800">DOCS</span></span>
            </div>
            <span class="text-sm text-gray-500 hidden sm:inline">100% Free PDF Tools</span>
        </header>

        <main class="flex-grow flex flex-col items-center justify-center px-4 py-12">
            <div class="max-w-xl w-full text-center">
                <h1 class="text-3xl sm:text-4xl font-extrabold text-gray-900 mb-3">Convert PDF to WORD</h1>
                <p class="text-gray-600 mb-8 text-base sm:text-lg">Convert your PDF to DOCX documents with incredible accuracy.</p>
                
                <form method="post" action="/convert" enctype="multipart/form-data" class="bg-white p-8 rounded-2xl shadow-md border border-gray-200">
                    <div id="drop-zone" class="border-2 border-dashed border-red-300 rounded-xl p-8 bg-red-50/30 hover:bg-red-50 transition cursor-pointer flex flex-col items-center justify-center">
                        <svg class="w-16 h-16 text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
                        </svg>
                        <p class="text-sm font-medium text-gray-700 mb-1">Click to select file or drag & drop here</p>
                        <p class="text-xs text-gray-400">PDF files up to 10MB</p>
                        <input type="file" id="file-input" name="file" accept=".pdf" required class="hidden">
                    </div>
                    
                    <p id="file-name" class="mt-4 text-sm font-semibold text-gray-600 hidden"></p>

                    <button type="submit" class="w-full mt-6 bg-red-600 hover:bg-red-700 text-white font-bold py-4 px-6 rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition active:translate-y-0 text-lg">
                        Convert to WORD
                    </button>
                </form>
            </div>
        </main>

        <footer class="bg-gray-900 text-gray-400 text-center py-4 text-sm border-t border-gray-800">
            <p>&copy; 2026 iLoveDOCS. Made for free conversions.</p>
        </footer>

        <script>
            const dropZone = document.getElementById('drop-zone');
            const fileInput = document.getElementById('file-input');
            const fileNameDisplay = document.getElementById('file-name');

            dropZone.addEventListener('click', () => fileInput.click());

            dropZone.addEventListener('dragover', (e) => {
                e.preventDefault();
                dropZone.classList.add('border-red-500', 'bg-red-50');
            });

            dropZone.addEventListener('dragleave', () => {
                dropZone.classList.remove('border-red-500', 'bg-red-50');
            });

            dropZone.addEventListener('drop', (e) => {
                e.preventDefault();
                dropZone.classList.remove('border-red-500', 'bg-red-50');
                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    updateFileName();
                }
            });

            fileInput.addEventListener('change', updateFileName);

            function updateFileName() {
                if (fileInput.files.length) {
                    fileNameDisplay.textContent = "Selected: " + fileInput.files[0].name;
                    fileNameDisplay.classList.remove('hidden');
                }
            }
        </script>
    </body>
    </html>
    '''
