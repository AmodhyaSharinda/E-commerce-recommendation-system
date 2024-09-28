import pymongo
from pymongo import MongoClient
import hashlib

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://sharinda72:200211@cluster1.gx7fq.mongodb.net/")
db = client["Clothing_DB"]  # Replace with your database name
collection = db["users"]
product_collection = db['product']   # Replace with your collection name

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

