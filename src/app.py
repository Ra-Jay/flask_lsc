from flask import Flask, render_template
from controllers.HomeController import input_file, output_file

from pathlib import Path
from flask_pymongo import PyMongo
from config import MONGO_URI
import secrets
from flask import session

from helpers.db import get_weights, insert_weights

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['UPLOAD_FOLDER'] = 'src/uploads'
app.config['ANALYZED_FOLDER'] = 'src/analyzed'
app.config['MONGO_URI'] = MONGO_URI
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

# Initialize PyMongo extension
mongo = PyMongo(app)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/')
def index():
    # Pre-defined weights
    loaded_weights = get_weights('lsc_v1')
    
    if loaded_weights is None:
        insert_weights('src\\pre-trained_weights\\yolov8s\\lsc_v1.pt', 'lsc_v1')
    
    session['loaded_weights'] = {
        'name': loaded_weights['name'] or 'lsc_v1',
        'path': loaded_weights['path'] or 'src\\pre-trained_weights\\yolov8s\\lsc_v1.pt'
    }
    
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/archived')
def archived():
    return render_template('archived.html')

@app.route('/help-and-support')
def helpandsupport():
    return render_template('helpsupport.html')

app.register_blueprint(input_file, mongo=mongo)
app.register_blueprint(output_file, mongo=mongo)

# Create the 'uploads' directory if it doesn't exist
uploads_dir = Path(app.config['UPLOAD_FOLDER'])
uploads_dir.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    app.run(debug=True)