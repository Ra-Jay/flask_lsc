from flask import Flask
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

app.register_blueprint(input_file, mongo=mongo)

# Create the 'uploads' directory if it doesn't exist
uploads_dir = Path(app.config['UPLOAD_FOLDER'])
uploads_dir.mkdir(parents=True, exist_ok=True)


if __name__ == '__main__':
    app.run(debug=True)