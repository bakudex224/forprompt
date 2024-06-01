from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import uuid

app = Flask(__name__)

# Configuración del espacio de almacenamiento
STORAGE_PATH = 'static/uploads'
STORAGE_LIMIT = 4 * 1024 * 1024 * 1024  # 4 GB

# Crear el directorio de almacenamiento si no existe
if not os.path.exists(STORAGE_PATH):
    os.makedirs(STORAGE_PATH)

# Estructura para almacenar información de los archivos
files = []

# Función para obtener el uso del almacenamiento
def get_storage_usage():
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(STORAGE_PATH):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

@app.route('/')
def index():
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    title = request.form['title']
    note = request.form['note']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if get_storage_usage() + len(file.read()) > STORAGE_LIMIT:
        return jsonify({'error': 'Storage limit exceeded'})

    file.seek(0)
    filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
    file.save(os.path.join(STORAGE_PATH, filename))

    filetype = 'image' if file.mimetype.startswith('image') else 'video'

    files.append({
        'id': str(uuid.uuid4()),
        'title': title,
        'note': note,
        'filename': filename,
        'filetype': filetype
    })

    return jsonify({'success': 'File uploaded successfully'})

@app.route('/file/<id>')
def get_file(id):
    for file in files:
        if file['id'] == id:
            return jsonify(file)
    return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
