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
from bson.binary import Binary

input_file = Blueprint('input_file', __name__)
output_file = Blueprint('output_file', __name__)

@input_file.route('/upload', methods=['GET', 'POST'])
def insert_input_file():
    from app import app
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if not allowed_file(file.filename):
            return redirect(request.url)
        
        filename = secure_filename(file.filename)
        
        # Check if input_file doesn't exist, then insert it. 
        # If it exists and its data is the same, return the existing input_file.
        # If it exists and its data is different, insert the new input_file.
        existing_input_file = get_input_file(filename)
        
        if existing_input_file is None:
            print("===============================")
            print("Uploading " + filename)
            start_time = time()  # Record the start time
            
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                print("===============================")
                print("Creating " + app.config['UPLOAD_FOLDER'] + " folder")
                os.makedirs(app.config['UPLOAD_FOLDER'])
                
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            file.save(path)
            
            elapsed_time = time() - start_time  # Calculate elapsed time
            print("===============================")
            print(f"New input file saved locally at {path} folder in {elapsed_time:.2f} seconds")
            
            start_time = time()  # Reset start time for the next step
            
            dimensions = get_file_dimensions(file)
            size = get_file_size(path)
            extension = get_file_extension(filename)

            elapsed_time = time() - start_time  # Calculate elapsed time
            print("===============================")
            print(f"File dimensions, size, and extension calculated in {elapsed_time:.2f} seconds")
            start_time = time()  # Reset start time for the next step
            
            with open(path, "rb") as image_file:
                input_binary_data = Binary(image_file.read())
                
            loaded_weights_id = session.get('loaded_weights')['_id']
            
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            input_file = InputFile(
                filename, 
                dimensions, 
                size, 
                extension, 
                input_binary_data, 
                loaded_weights_id, 
                current_date, 
                current_date, 
                None
            )
            
            session['input_file'] = input_file.__dict__
            
            start_time = time()
            
            insert_input_file()
            
            elapsed_time = time() - start_time
            print("===============================")
            print(f"Inserted new input file to mongodb in {elapsed_time:.2f} seconds")
            print("===============================")
            
            return render_template('index.html', input_file=input_file)
        else:
            print("===============================")
            print("Fetching " + filename)
            start_time = time()
            
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                print("===============================")
                print("Creating " + app.config['UPLOAD_FOLDER'] + " folder")
                os.makedirs(app.config['UPLOAD_FOLDER'])
            
            input_file = InputFile(
                existing_input_file['name'],
                existing_input_file['dimensions'],
                existing_input_file['size'],
                existing_input_file['extension'],
                existing_input_file['data'],
                existing_input_file['weight_id'],
                existing_input_file['created_at'],
                existing_input_file['updated_at'],
                existing_input_file['deleted_at']
            )
            
            session['input_file'] = input_file.__dict__
            
            stream = io.BytesIO(existing_input_file['data'])
            input_image = Image.open(stream)
            input_image.save(app.config['UPLOAD_FOLDER'] + '/' + existing_input_file['name'])
            
            elapsed_time = time() - start_time  # Calculate elapsed time
            print("===============================")
            print(f"Existing image from mongodb saved to {app.config['UPLOAD_FOLDER']}/{existing_input_file['name']} in {elapsed_time:.2f} seconds")
            print("===============================")
            
            return render_template('index.html', input_file=input_file)

    return render_template('index.html')

@input_file.route('/analyze', methods=['GET', 'POST'])
def insert_output_file():
    from app import app
    if request.method == 'POST':
        input_file_data = session.get('input_file')

        if input_file_data is None:
            # Redirect to the homepage or show an error message
            return redirect(url_for('input_file.upload'))

        # Access the relevant data from input_file_data dictionary
        filename = input_file_data['name']
        
        # Check if output_file doesn't exist, then insert it.
        # If it exists and its data is the same, return the existing output_file.
        # If it exists and its data is different, insert the new output_file.
        existing_output_file = get_output_file(filename)
        
        if existing_output_file is None:
            print("===============================")
            print("Analyzing " + filename)
            start_time = time()
            
            # Predict the image using the trained YOLO model
            result = analyze_image(filename)
            path = result[0].path
            
            session['output_date'] = path.split('/')[2]
            
            elapsed_time = time() - start_time
            print("\n===============================")
            print(f"Image analyzed in {elapsed_time:.2f} seconds")
            print("New output file saved to " + path + " folder")
            
            start_time = time()
            
            classification = "No Good" if torch.tensor(result[0].boxes.cls).item() > 0 else "Good"
            accuracy = round(torch.tensor(result[0].boxes.conf).item(),2 )
            error_rate = round(1 - accuracy, 2)
            
            elapsed_time = time() - start_time
            print("===============================")
            print(f"Classification, accuracy, and error rate calculated in {elapsed_time:.2f} seconds")
            
            with open(path, "rb") as image_file:
                input_binary_data = Binary(image_file.read())
            
            input_id = get_input_file(filename)['_id']
            
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            
            output_file = OutputFile(
                filename,
                classification,
                accuracy,
                error_rate,
                input_binary_data,
                input_id,
                current_date,
                current_date,
                None
            )
            
            session['output_file'] = output_file.__dict__
            
            start_time = time()
            
            insert_output_file()
            
            elapsed_time = time() - start_time
            print("===============================")
            print(f"Inserted new output file to mongodb in {elapsed_time:.2f} seconds")
            print("===============================")
            
            return render_template('index.html', input_file=input_file_data, output_file=output_file)
        else:
            print("===============================")
            print("Fetching " + existing_output_file['name'])
            start_time = time()
            
            older_date = existing_output_file['created_at'].replace(':', '-').replace(' ', '_')

            if not os.path.exists(app.config['PREDICTIONS_FOLDER'] + "/" +  older_date):
                print("===============================")
                print("Creating " + app.config['PREDICTIONS_FOLDER'] + " folder")
                os.makedirs(app.config['PREDICTIONS_FOLDER'] + "/" +  older_date)
                
            older_path = app.config['PREDICTIONS_FOLDER'] + "/" + older_date + '/' + existing_output_file['name']
            
            session['output_date'] = older_date
            
            output_file = OutputFile(
                existing_output_file['name'],
                existing_output_file['classification'],
                existing_output_file['accuracy'],
                existing_output_file['error_rate'],
                existing_output_file['data'],
                existing_output_file['input_id'],
                existing_output_file['created_at'],
                existing_output_file['updated_at'],
                existing_output_file['deleted_at']
            )
            
            session['output_file'] = output_file.__dict__
            
            stream = io.BytesIO(existing_output_file['data'])
            output_image = Image.open(stream)
            output_image.save(older_path)
            
            elapsed_time = time() - start_time
            print("===============================")
            print(f"Existing image from mongodb saved to {older_path} in {elapsed_time:.2f} seconds")
            print("===============================")
            
            return render_template('index.html', input_file=input_file_data, output_file=output_file)
    
    return render_template('index.html')

@input_file.route('/uploads/<filename>', methods=['GET'])
def get_file(filename):
    return send_from_directory('uploads', filename)

@output_file.route('/predictions/' + '<date>' + '/<filename>', methods=['GET'])
def get_file(filename, date):
    return send_from_directory('predictions/' + date + '/', filename)