#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from flask import make_response, jsonify
from ultralytics import YOLO
from datetime import datetime
from PIL import Image

def toDictionaryArray(data):
    x = []
    for dt in data:
        a = {}
        keys = dt.keys()
        for d in keys:
            a[d] = str(dt[d])
        x.append(a)
    return x

def sendResponse(result):
    resp = make_response(jsonify(result))
    resp.mimetype = 'application/json'
    return resp

def analyze_image(filename):
    from app import app
    model = YOLO('src\\pre-trained_weights\\yolov8s\\lsc_v1.pt')
    file_path = os.path.join('src\\uploads\\', filename)
    now = datetime.now()
    date_time_str = now.strftime('%Y-%m-%d_%H-%M')
    result = model.predict(source=file_path, show=False, conf=0.20, project="src/predictions", name=date_time_str, save=True)
    print("-----------------------------------------------------")
    # analyzed_folder = "ANALYZED_FOLDER"
    # analyzed_file_path = os.path.join(analyzed_folder, filename)
    # os.makedirs(analyzed_folder, exist_ok=True)
    # shutil.move(file_path, analyzed_file_path)
    result[0].path = "src/predictions/" + date_time_str + "/" + filename
    
    return result

def allowed_file(filename):
    from app import app
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_file_dimensions(filename):
    try:
        with Image.open(filename) as img:
            width, height = img.size
            return f"{width}x{height}"
    except Exception as e:
        print(f"Error while getting dimensions: {e}")
        return None

def get_file_size(filename):
    try:
        file_size = os.path.getsize(filename)
        # Convert bytes to kilobytes (KB)
        size_in_kb = file_size / 1024
        return f"{size_in_kb:.2f} kB"
    except Exception as e:
        return f"Error while getting file size: {e}"

def get_file_extension(filename):
    return filename.rsplit('.', 1)[1].lower()