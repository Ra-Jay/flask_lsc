from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION_WEIGHTS, MONGO_COLLECTION_INPUT_FILES, MONGO_COLLECTION_OUTPUT_FILES
from bson.binary import Binary
import io
from PIL import Image
import torch

def insert_input_file(input_image_path):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]  # Connect to MongoDB using the URI and database name
    with open(input_image_path, "rb") as image_file:
        input_image = image_file.read()
    
    last_slash_index = image_file.name.rfind("\\")
    filtered_name = image_file.name[last_slash_index + 1:]
    image_document = {"name": filtered_name, "data": Binary(input_image)}
    mongo[MONGO_COLLECTION_INPUT_FILES].insert_one(image_document)
    
def get_input_file(image_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    document = mongo[MONGO_COLLECTION_INPUT_FILES].find_one({"name": image_name})
    binary_data = document["data"]

    stream = io.BytesIO(binary_data)

    image = Image.open(stream)

    # Save the image to a file
    # Not yet necessary saving the file locally, but for when history page is implemented
    # Can either be saving or returning a value/image to be displayed in the frontend
    # If saving, uncomment the following line but make sure to create the folder first
    # image.save('src/mongodb/input_images/' + image_name)

def insert_output_file(predicted_image_path):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]  # Connect to MongoDB using the URI and database name
    with open(predicted_image_path, "rb") as image_file:
        predicted_image = image_file.read()
    
    last_slash_index = image_file.name.rfind("/")
    filtered_name = image_file.name[last_slash_index + 1:]
    image_document = {"name": filtered_name, "data": Binary(predicted_image)}
    mongo[MONGO_COLLECTION_OUTPUT_FILES].insert_one(image_document)

# This method was for testing purposes to decode the binary data and save/display as an image.
def get_output_file(image_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    document = mongo[MONGO_COLLECTION_OUTPUT_FILES].find_one({"name": image_name})
    binary_data = document["data"]

    stream = io.BytesIO(binary_data)

    image = Image.open(stream)

    # Save the image to a file
    # Not yet necessary saving the file locally, but for when history page is implemented
    # Can either be saving or returning a value/image to be displayed in the frontend
    # If saving, uncomment the following line but make sure to create the folder first
    # image.save('src/mongodb/predicted_images/' + image_name)
    
def insert_weights(pt_file_path, model_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]

    # Read the PyTorch model file
    with open(pt_file_path, 'rb') as pt_file:
        pt_model_data = pt_file.read()

    # Convert the model data to BSON binary format
    bson_model_data = Binary(pt_model_data)

    # Create a document for the model and insert it into the MongoDB collection
    model_document = {"name": model_name, "data": bson_model_data}
    mongo[MONGO_COLLECTION_WEIGHTS].insert_one(model_document)

def get_weights(model_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]

    # Find the model document by name
    model_document = mongo[MONGO_COLLECTION_WEIGHTS].find_one({"name": model_name})

    if model_document is None:
        raise ValueError(f"Model '{model_name}' not found in the database.")

    # Retrieve the model data from the document
    bson_model_data = model_document["data"]

    # Convert the BSON binary data back to bytes
    pt_model_data = bson_model_data

    # Load the PyTorch model from the bytes data
    model = torch.load(io.BytesIO(pt_model_data))

    return model

# Example usage:
# insert_pt_model('/path/to/your/model.pt', 'MyPyTorchModel')
# loaded_model = load_pt_model('MyPyTorchModel')