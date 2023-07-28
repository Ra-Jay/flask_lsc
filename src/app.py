from flask import Flask, render_template
from controllers.HomeController import input_file
from pathlib import Path
from flask_pymongo import PyMongo
from config import MONGO_URI

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'src/uploads'
app.config['MONGO_URI'] = MONGO_URI
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions

# Initialize PyMongo extension
mongo = PyMongo(app)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/archived')
def archived():
    return render_template('archived.html')

@app.route('/helpandsupport')
def helpandsupport():
    return render_template('helpsupport.html')

app.register_blueprint(input_file, mongo=mongo)

# Create the 'uploads' directory if it doesn't exist
uploads_dir = Path(app.config['UPLOAD_FOLDER'])
uploads_dir.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    app.run(debug=True)