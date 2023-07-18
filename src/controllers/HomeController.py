import torch
import shutil
import os
from models.InputFile import InputFile
from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename
from helpers.db import insert_data
from helpers.Utility import analyze_image, get_file_dimensions, get_file_extension, allowed_file

input_file = Blueprint('input_file', __name__)

@input_file.route('/', methods=['GET', 'POST'])
def upload():
    from app import app
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if not allowed_file(file.filename):
            return redirect(request.url)

        print("===============================")
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Predict the image using the trained YOLO model
        print("-------------------------------------------")
        print(filename)
        analyze_image(filename)

        dimensions = get_file_dimensions(filename)
        size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        extension = get_file_extension(filename)
        input_file = InputFile(dimensions, size, extension, filename)

        # Save the image data to MongoDB
        image_data = {
            'dimensions': dimensions,
            'size': size,
            'extension': extension,
            'filename': filename
        }
        #insert_data(image_data)

        return render_template('index.html', input_file=input_file)

    return render_template('index.html')

@input_file.route('/uploads/<filename>')
def get_uploaded_image(filename):
    return send_from_directory('uploads', filename)

@input_file.route('/analyzed/<filename>')
def get_analyzed_image(filename):
    app = current_app._get_current_object()
    return send_from_directory(app.config['ANALYZED_FOLDER'], filename)

