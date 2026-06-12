import os
from flask import Flask, render_template, request, send_file
from pdf2docx import Converter

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'

@app.route('/')
def index():
    return '''
    <!doctype html>
    <html>
    <head>
        <title>Free PDF to Word Converter</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f4f4f9; }
            .box { border: 2px dashed #ccc; padding: 30px; display: inline-block; background: white; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
            input[type="submit"] { background: #e74c3c; color: white; border: none; padding: 10px 20px; cursor: pointer; border-radius: 5px; margin-top: 15px; font-weight: bold;}
            input[type="submit"]:hover { background: #c0392b; }
        </style>
    </head>
    <body>
        <div class="box">
            <h2>Convert PDF to Word</h2>
            <form method="post" action="/convert" enctype="multipart/form-data">
              <input type="file" name="file" accept=".pdf" required><br>
              <input type="submit" value="Convert Now">
            </form>
        </div>
    </body>
    </html>
    '''

@app.route('/convert', methods=['POST'])
def convert_pdf():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    if file.filename == '' or not file.filename.endswith('.pdf'):
        return "Invalid file selection", 400

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)
    
    docx_filename = file.filename.replace('.pdf', '.docx')
    docx_path = os.path.join(UPLOAD_FOLDER, docx_filename)
    
    try:
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        return send_file(docx_path, as_attachment=True)
    except Exception as e:
        return f"An error occurred during conversion: {str(e)}", 500
    finally:
        if os.path.exists(pdf_path): os.remove(pdf_path)

if __name__ == '__main__':
    app.run(debug=True)