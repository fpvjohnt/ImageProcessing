from flask import Flask, request, render_template, jsonify
import os
import shutil
from werkzeug.utils import secure_filename
from PIL import Image
import numpy as np
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to apply the filter to the uploaded image
def apply_filter(filter_type):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg')
    image = cv2.imread(image_path)

    if filter_type == 'grayscale':
        filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif filter_type == 'invert':
        filtered_image = cv2.bitwise_not(image)
    else:
        return None

    filtered_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'filtered_image.jpg')
    filtered_image = Image.fromarray(filtered_image)  # Convert to PIL Image
    filtered_image.save(filtered_image_path)  # Save the image using PIL

    return filtered_image_path

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'uploaded_image.jpg'))
        folders = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))]
        return jsonify({'success': 'File uploaded successfully', 'folders': folders})
    else:
        return jsonify({'error': 'Invalid file format'})

@app.route('/create_folder', methods=['POST'])
def create_folder():
    folder_name = request.json.get('folder_name')
    if not folder_name:
        return jsonify({'error': 'Folder name is required'})

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return jsonify({'success': 'Folder created successfully'})
    else:
        return jsonify({'error': 'Folder already exists'})

@app.route('/get_folders', methods=['GET'])
def get_folders():
    folders = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if os.path.isdir(os.path.join(app.config['UPLOAD_FOLDER'], f))]
    return jsonify({'folders': folders})

@app.route('/delete_folder', methods=['POST'])
def delete_folder():
    folder_name = request.json.get('folder_name')
    if not folder_name:
        return jsonify({'error': 'Folder name is required'})

    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_name)

    # Check if the folder exists before attempting to delete it
    if os.path.exists(folder_path):
        try:
            # Use shutil to delete the folder and its contents
            shutil.rmtree(folder_path)
            return jsonify({'success': 'Folder deleted successfully'})
        except Exception as e:
            return jsonify({'error': f'Error deleting folder: {str(e)}'})
    else:
        return jsonify({'error': 'Folder not found'})

@app.route('/get_folder_contents/<path:folder_path>', methods=['GET'])
def get_folder_contents(folder_path):
    folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder_path)
    if os.path.exists(folder_path):
        contents = []
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                contents.append({'name': item, 'type': 'folder', 'path': os.path.relpath(item_path, app.config['UPLOAD_FOLDER'])})
            else:
                contents.append({'name': item, 'type': 'file', 'path': os.path.relpath(item_path, app.config['UPLOAD_FOLDER'])})
        return jsonify({'contents': contents})
    else:
        return jsonify({'error': 'Folder not found'})

@app.route('/apply_filter', methods=['POST'])
def apply_filter_endpoint():
    filter_type = request.json.get('filter_type')
    if not filter_type:
        return jsonify({'error': 'Filter type is required'})

    filtered_image_path = apply_filter(filter_type)

    if filtered_image_path:
        return jsonify({'success': 'Filter applied successfully', 'filtered_image': filtered_image_path})
    else:
        return jsonify({'error': 'Invalid filter type'})

if __name__ == '__main__':
    app.run(debug=True)