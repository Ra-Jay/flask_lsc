from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

def insert_data(image_data):
    mongo = MongoClient(MONGO_URI)[MONGO_DB]  # Connect to MongoDB using the URI and database name
    mongo[MONGO_COLLECTION].insert_one(image_data)
