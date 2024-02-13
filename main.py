from urllib.parse import quote_plus

import certifi as certifi
import pymongo
username = quote_plus('amih77')
password = quote_plus('amihaizzivan')
uri = f"mongodb+srv://{username}:{password}@cluster0.1wobhuh.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())

db = client['your_database_name']

# Explicitly create a collection named 'explicit_collection'
collection = db.create_collection('explicit_collection')

print("Explicit collection created!")


public = "sieojtzn"

private = "07a1bda1-6de4-4399-9ecc-08d2ad9036de"