import torch
import os
import io
from models.InputFile import InputFile
from models.OutputFile import OutputFile
from flask import Blueprint, render_template, request, redirect, url_for, current_app, send_from_directory
from werkzeug.utils import secure_filename
from helpers.db import insert_input_file, get_input_file, insert_output_file, get_output_file, insert_weights, get_weights
from datetime import datetime
from helpers.Utility import analyze_image, get_file_dimensions, get_file_size, get_file_extension, allowed_file
from flask import session
from time import time
from PIL import Image

input_file = Blueprint('input_file', __name__)
output_file = Blueprint('output_file', __name__)

@input_file.route('/upload', methods=['GET', 'POST'])
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
        start_time = time()  # Record the start time
        
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        
        elapsed_time = time() - start_time  # Calculate elapsed time
        print(f"File saved in {elapsed_time:.2f} seconds")
        start_time = time()  # Reset start time for the next step
        
        dimensions = get_file_dimensions(file)
        size = get_file_size(path)
        extension = get_file_extension(filename)

        elapsed_time = time() - start_time  # Calculate elapsed time
        print(f"File dimensions, size, and extension calculated in {elapsed_time:.2f} seconds")
        start_time = time()  # Reset start time for the next step
        
        input_file = InputFile(dimensions, size, extension, filename)
        session['input_file'] = {
            'dimensions': dimensions,
            'size': size,
            'extension': extension,
            'filename': filename,
        }
        
        # Check if input_file doesn't exist, then insert it. 
        # If it exists and its data is the same, return the existing input_file.
        # If it exists and its data is different, insert the new input_file.
        existing_input_file = get_input_file(filename)
        if existing_input_file is None:
            insert_input_file(path)
        else:
            if existing_input_file['dimensions'] != dimensions or existing_input_file['size'] != size or existing_input_file['extension'] != extension:
                insert_input_file(path)
            else:
                # Create a folder if the upload folder doesn't exist and store the image there
                if not os.path.exists(app.config['UPLOAD_FOLDER']):
                    os.makedirs(app.config['UPLOAD_FOLDER'])
                
                input_file = InputFile(existing_input_file['dimensions'], existing_input_file['size'], existing_input_file['extension'], existing_input_file['name'])
                stream = io.BytesIO(existing_input_file['data'])
                input_image = Image.open(stream)
                input_image.save(app.config['UPLOAD_FOLDER'] + '/' + existing_input_file['name'])
                
                elapsed_time = time() - start_time  # Calculate elapsed time
                print(f"Existing image from mongodb saved to {app.config['UPLOAD_FOLDER']}/{existing_input_file['name']} in {elapsed_time:.2f} seconds")
                print("===============================")
                
                return render_template('index.html', input_file=input_file)
                
        
        elapsed_time = time() - start_time  # Calculate elapsed time
        print(f"Input file object created and inserted to mongodb in {elapsed_time:.2f} seconds")
        print("===============================")
        
        return render_template('index.html', input_file=input_file)

    return render_template('index.html')

@input_file.route('/analyze', methods=['GET', 'POST'])
def analyze():
    from app import app
    if request.method == 'POST':
        input_file_data = session.get('input_file')

        if input_file_data is None:
            # Redirect to the homepage or show an error message
            return redirect(url_for('input_file.upload'))

        # Access the relevant data from input_file_data dictionary
        filename = input_file_data['filename']
        
        # Predict the image using the trained YOLO model
        print("===============================")
        print("Analyzing " + filename)
        start_time = time() 
        
        result = analyze_image(filename)
        
        elapsed_time = time() - start_time
        print("\n===============================")
        print(f"Image analyzed in {elapsed_time:.2f} seconds")
        
        path = result[0].path
        print("Image saved to " + path)
        print("===============================")
        start_time = time()
        
        classification = "No Good" if torch.tensor(result[0].boxes.cls).item() > 0 else "Good"
        accuracy = round(torch.tensor(result[0].boxes.conf).item(),2 )
        error_rate = round(1 - accuracy, 2)
        
        elapsed_time = time() - start_time
        print("===============================")
        print(f"Classification, accuracy, and error rate calculated in {elapsed_time:.2f} seconds")
        print("===============================")
        
        start_time = time()
        
        output_file = OutputFile(classification, accuracy, error_rate, path, filename)
        session['output_file'] = {
            'classification': classification,
            'accuracy': accuracy,
            'error_rate': error_rate,
            'path': path,
            'filename': filename
        }
        
        # Check if output_file doesn't exist, then insert it.
        # If it exists and its data is the same, return the existing output_file.
        # If it exists and its data is different, insert the new output_file.
        existing_output_file = get_output_file(filename)
        if existing_output_file is None:
            insert_output_file(path)
        else:
            if existing_output_file['classification'] != classification or existing_output_file['accuracy'] != accuracy or existing_output_file['error_rate'] != error_rate:
                insert_output_file(path)
            else:
                older_date = existing_output_file['created_at'].replace(':', '-').replace(' ', '_')[:-3]
                # Create a folder for the older date if it doesn't exist and store the image there
                if not os.path.exists(app.config['PREDICTIONS_FOLDER'] + "/" +  older_date):
                    os.makedirs(app.config['PREDICTIONS_FOLDER'] + "/" +  older_date)
                    
                older_path = app.config['PREDICTIONS_FOLDER'] + "/" + older_date + '/' + existing_output_file['name']
                output_file = OutputFile(existing_output_file['classification'], existing_output_file['accuracy'], existing_output_file['error_rate'], older_path, existing_output_file['name'])
                stream = io.BytesIO(existing_output_file['data'])
                output_image = Image.open(stream)
                output_image.save(older_path)
                elapsed_time = time() - start_time
                print(f"Existing image from mongodb saved to {older_path} in {elapsed_time:.2f} seconds")
                print("===============================")
                
                return render_template('index.html', input_file=input_file_data, output_file=output_file)
        
        elapsed_time = time() - start_time
        print(f"Output file object created and inserted to mongodb in {elapsed_time:.2f} seconds")
        print("===============================")
        
        return render_template('index.html', input_file=input_file_data, output_file=output_file)
    
    return render_template('index.html')

@input_file.route('/uploads/<filename>', methods=['GET'])
def get_from_local(filename):
    return send_from_directory('uploads', filename)

@output_file.route('/predictions/' + datetime.now().strftime('%Y-%m-%d_%H-%M') + '/<filename>', methods=['GET'])
def get_from_local(filename):
    return send_from_directory('predictions/' + datetime.now().strftime('%Y-%m-%d_%H-%M'), filename)

