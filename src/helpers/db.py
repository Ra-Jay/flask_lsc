from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION_WEIGHTS, MONGO_COLLECTION_INPUT_FILES, MONGO_COLLECTION_OUTPUT_FILES
from bson.binary import Binary
import io
from PIL import Image
from flask import session

def insert_input_file(input_image_path):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]  # Connect to MongoDB using the URI and database name
    with open(input_image_path, "rb") as image_file:
        input_image = image_file.read()
    
    current_input_file = session.get('input_file')
    
    image_document = {
        "_id": mongo[MONGO_COLLECTION_INPUT_FILES].count_documents({}) + 1,
        "name": current_input_file['filename'], 
        "dimensions": current_input_file['dimensions'], 
        "size": current_input_file['size'], 
        "extension": current_input_file['extension'], 
        "data": Binary(input_image),
        "weight_id": get_weights('LSCModel')['_id']
    }
    mongo[MONGO_COLLECTION_INPUT_FILES].insert_one(image_document)
    
def get_input_file(image_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    return mongo[MONGO_COLLECTION_INPUT_FILES].find_one({"name": image_name})
    
    # Save the image to a file
    # Not yet necessary saving the file locally, but for when history page is implemented
    # Can either be saving or returning a value/image to be displayed in the frontend
    # If saving, uncomment the following line but make sure to create the folder first
    # binary_data = document["data"]
    # stream = io.BytesIO(binary_data)
    # image = Image.open(stream)
    # image.save('src/mongodb/input_images/' + image_name)

def insert_output_file(predicted_image_path):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]  # Connect to MongoDB using the URI and database name
    with open(predicted_image_path, "rb") as image_file:
        predicted_image = image_file.read()
    
    current_output_file = session.get('output_file')
    
    # Add input id to output file
    image_document = {
        "_id": mongo[MONGO_COLLECTION_OUTPUT_FILES].count_documents({}) + 1,
        "name": current_output_file['filename'],
        "classification": current_output_file['classification'],
        "accuracy": current_output_file['accuracy'],
        "error_rate": current_output_file['error_rate'],
        "data": Binary(predicted_image),
        "input_id": get_input_file(current_output_file['filename'])['_id']
    }
    mongo[MONGO_COLLECTION_OUTPUT_FILES].insert_one(image_document)

# This method was for testing purposes to decode the binary data and save/display as an image.
def get_output_file(image_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    return mongo[MONGO_COLLECTION_OUTPUT_FILES].find_one({"name": image_name})
    
    # Save the image to a file
    # Not yet necessary saving the file locally, but for when history page is implemented
    # Can either be saving or returning a value/image to be displayed in the frontend
    # If saving, uncomment the following line but make sure to create the folder first
    # binary_data = document["data"]
    # stream = io.BytesIO(binary_data)
    # image = Image.open(stream)
    # image.save('src/mongodb/predicted_images/' + image_name)
    
def insert_weights(pt_file_path, model_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    
    # best.pt file is too large (22mb) to be stored in MongoDB (16mb maximum), so we will store its path instead
    # Read the PyTorch model file
    # with open(pt_file_path, 'rb') as pt_file:
    #     pt_model_data = pt_file.read()

    # Convert the model data to BSON binary format
    # bson_model_data = Binary(pt_model_data)

    # Create a document for the model and insert it into the MongoDB collection
    now = datetime.now()
    date_time_str = now.strftime('%Y-%m-%d_%H-%M')
    
    model_document = {
        "_id": mongo[MONGO_COLLECTION_WEIGHTS].count_documents({}) + 1,
        "name": model_name, 
        "date_generated": date_time_str,
        "path": pt_file_path
    }
    mongo[MONGO_COLLECTION_WEIGHTS].insert_one(model_document)

def get_weights(model_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]

    # Find the model document by name
    model_document = mongo[MONGO_COLLECTION_WEIGHTS].find_one({"name": model_name})
    
    # Return the model document
    return model_document