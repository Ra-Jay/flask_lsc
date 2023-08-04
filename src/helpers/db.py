from datetime import datetime
from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION_WEIGHTS, MONGO_COLLECTION_INPUT_FILES, MONGO_COLLECTION_OUTPUT_FILES
from bson.binary import Binary
import io
from PIL import Image
from flask import session

def insert_input_file():
    mongo = MongoClient(MONGO_URI)[MONGO_DB]  # Connect to MongoDB using the URI and database name
    current_input_file = session.get('input_file')
    
    image_document = {
        "_id": mongo[MONGO_COLLECTION_INPUT_FILES].count_documents({}) + 1,
        "name": current_input_file['name'], 
        "dimensions": current_input_file['dimensions'], 
        "size": current_input_file['size'], 
        "extension": current_input_file['extension'], 
        "data": current_input_file['data'],
        "weight_id": current_input_file['weight_id'],
        "created_at": current_input_file['created_at'],
        "updated_at": current_input_file['updated_at'],
        "deleted_at": current_input_file['deleted_at']
    }
    
    mongo[MONGO_COLLECTION_INPUT_FILES].insert_one(image_document)
    
def get_input_file(image_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    return mongo[MONGO_COLLECTION_INPUT_FILES].find_one({"name": image_name})

def insert_output_file():
    mongo = MongoClient(MONGO_URI)[MONGO_DB]  # Connect to MongoDB using the URI and database name
    
    current_output_file = session.get('output_file')
    
    # Add input id to output file
    image_document = {
        "_id": mongo[MONGO_COLLECTION_OUTPUT_FILES].count_documents({}) + 1,
        "name": current_output_file['name'],
        "classification": current_output_file['classification'],
        "accuracy": current_output_file['accuracy'],
        "error_rate": current_output_file['error_rate'],
        "data": current_output_file['data'],
        "input_id": current_output_file['input_id'],
        "created_at": current_output_file['created_at'],
        "updated_at": current_output_file['updated_at'],
        "deleted_at": current_output_file['deleted_at']
    }
    mongo[MONGO_COLLECTION_OUTPUT_FILES].insert_one(image_document)

def get_output_file(image_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    return mongo[MONGO_COLLECTION_OUTPUT_FILES].find_one({"name": image_name})
    
def insert_weights():
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    
    current_weights = session.get('loaded_weights')
    
    # best.pt file is too large (22mb) to be stored in MongoDB (16mb maximum), so we will store its path instead
    # Read the PyTorch model file
    # with open(pt_file_path, 'rb') as pt_file:
    #     pt_model_data = pt_file.read()

    # Convert the model data to BSON binary format
    # bson_model_data = Binary(pt_model_data)

    # Create a document for the model and insert it into the MongoDB collection
    
    # trained_at here was the date the model was trained
    # This weight was copied from LSC_Inspector_Training_Model.ipynb in the repository
    # https://github.com/kerrlabajo/cs346-ml.net-lsc-inspector/tree/enhancement/refactor/LSC_Intellysis/runs/detect/train7/weights/best.pt
    model_document = {
        "_id": mongo[MONGO_COLLECTION_WEIGHTS].count_documents({}) + 1,
        "name": current_weights['name'],
        "path": current_weights['path'],
        "trained_at": current_weights['trained_at'],
        "created_at": current_weights['created_at'],
        "updated_at": current_weights['updated_at'],
        "deleted_at": current_weights['deleted_at']
    }
    
    return mongo[MONGO_COLLECTION_WEIGHTS].insert_one(model_document)

def get_weights(model_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]

    return mongo[MONGO_COLLECTION_WEIGHTS].find_one({"name": model_name})