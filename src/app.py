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
app.config['PREDICTIONS_FOLDER'] = 'src/predictions'
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
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        weights = Weights(
            'lsc_v1',
            'src\\pre-trained_weights\\yolov8s\\lsc_v1.pt',
            "2023-05-18 08:46",
            current_date,
            current_date,
            None
        )
        
        session['loaded_weights'] = weights.__dict__
        
        added_weights = insert_weights()
        
        session['loaded_weights']['_id'] = added_weights.inserted_id
    else:
        session['loaded_weights'] = {
            '_id': loaded_weights['_id'],
            'name': loaded_weights['name'],
            'path': loaded_weights['path'],
            'trained_at': loaded_weights['trained_at'],
            'created_at': loaded_weights['created_at'],
            'updated_at': loaded_weights['updated_at'],
            'deleted_at': loaded_weights['deleted_at']
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