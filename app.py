from flask import Flask, request, render_template_string, send_from_directory
import os
import urllib.parse

app = Flask(__name__)

# Absolute path set kiya hai
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Aapke platform ka Frontend (HTML/CSS)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cloud Hosting Platform</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 50px; text-align: center; }
        .box { background: white; max-width: 500px; margin: auto; padding: 30px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        h2 { color: #333; margin-top: 0; }
        input[type="file"] { margin: 20px 0; padding: 10px; border: 1px dashed #ccc; width: 90%; cursor: pointer; }
        button { background: #0066cc; color: white; border: none; padding: 12px 24px; font-size: 16px; border-radius: 6px; cursor: pointer; transition: 0.3s; }
        button:hover { background: #0052a3; }
        .result { margin-top: 25px; padding: 15px; background: #e6f7ff; border: 1px solid #91d5ff; border-radius: 6px; display: inline-block; width: 90%; word-wrap: break-word;}
        a { color: #0066cc; font-weight: bold; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="box">
        <h2>🚀 Upload File & Get Link</h2>
        <form action="/upload" method="post" enctype="multipart/form-data">
            <input type="file" name="file" required>
            <br>
            <button type="submit">Upload File</button>
        </form>
        
        {% if file_url %}
        <div class="result">
            ✅ <b>File Uploaded Successfully!</b><br><br>
            Aapka Link: <br>
            <a href="{{ file_url }}" target="_blank">{{ file_url }}</a>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "File nahi mili!", 400
    
    file = request.files['file']
    
    if file.filename == '':
        return "Koi file select nahi ki gayi!", 400
        
    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Render par live link generate hoga
        file_url = request.host_url + 'site/' + urllib.parse.quote(filename)
        return render_template_string(HTML_TEMPLATE, file_url=file_url)

@app.route('/site/<path:filename>')
def serve_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # Render khud ka port deta hai, isliye humne os.environ.get lagaya hai
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
