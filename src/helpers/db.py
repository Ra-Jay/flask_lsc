from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from bson.binary import Binary
import io
from PIL import Image

def insert_predicted_image(predicted_image_path):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]  # Connect to MongoDB using the URI and database name
    with open(predicted_image_path, "rb") as image_file:
        predicted_image = image_file.read()
    
    last_slash_index = image_file.name.rfind("/")
    filtered_name = image_file.name[last_slash_index + 1:]
    image_document = {"name": filtered_name, "data": Binary(predicted_image)}
    mongo[MONGO_COLLECTION].insert_one(image_document)

# This method was for testing purposes to decode the binary data and save/display as an image.
def get_predicted_image(image_name):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]
    document = mongo[MONGO_COLLECTION].find_one({"name": image_name})
    binary_data = document["data"]

    stream = io.BytesIO(binary_data)

    image = Image.open(stream)

    # Save the image to a file
    # Not yet necessary saving the file locally, but for when history page is implemented
    # Can either be saving or returning a value/image to be displayed in the frontend
    # If saving, uncomment the following line but make sure to create the folder first
    # image.save('src/mongodb/predicted_images/' + image_name)