import torch
import os
from models.InputFile import InputFile
from models.OutputFile import OutputFile
from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename
from helpers.db import insert_input_file, get_input_file, insert_output_file, get_output_file, insert_weights, get_weights
from datetime import datetime
from helpers.Utility import analyze_image, get_file_dimensions, get_file_size, get_file_extension, allowed_file
from flask import session

input_file = Blueprint('input_file', __name__)
output_file = Blueprint('output_file', __name__)

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

        dimensions = get_file_dimensions(file)
        size = get_file_size(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        extension = get_file_extension(filename)

        input_file = InputFile(dimensions, size, extension, filename)
        session['input_file'] = {
            'dimensions': dimensions,
            'size': size,
            'extension': extension,
            'filename': filename
        }
        
        # Check if weight already exists in the database
        if get_weights('LSCModel') is None:
            insert_weights('src\\best.pt', 'LSCModel')
        
        insert_input_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        return render_template('index.html', input_file=input_file)

    return render_template('index.html')

@input_file.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        input_file_data = session.get('input_file')

        if input_file_data is None:
            # Redirect to the homepage or show an error message
            return redirect(url_for('input_file.upload'))

        # Access the relevant data from input_file_data dictionary
        filename = input_file_data['filename']
        
        # Predict the image using the trained YOLO model
        print(filename)
        result = analyze_image(filename)
        print("result: ---------------------------------")
        print(result[0].boxes)
        path = result[0].path
        
        classification = "No Good" if torch.tensor(result[0].boxes.cls).item() > 0 else "Good"
        accuracy = round(torch.tensor(result[0].boxes.conf).item(),2 )
        error_rate = round(1 - accuracy, 2)
        
        output_file = OutputFile(classification, accuracy, error_rate, path, filename)
        session['output_file'] = {
            'classification': classification,
            'accuracy': accuracy,
            'error_rate': error_rate,
            'path': path,
            'filename': filename
        }
        
        insert_output_file(path)
        
        return render_template('index.html', input_file=input_file_data, output_file=output_file)
    
    return render_template('index.html')

@input_file.route('/uploads/<filename>', methods=['GET'])
def get_from_local(filename):
    return send_from_directory('uploads', filename)

@output_file.route('/predictions/' + datetime.now().strftime('%Y-%m-%d_%H-%M') + '/<filename>', methods=['GET'])
def get_from_local(filename):
    return send_from_directory('predictions/' + datetime.now().strftime('%Y-%m-%d_%H-%M'), filename)

