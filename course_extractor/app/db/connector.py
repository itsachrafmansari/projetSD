from pymongo.mongo_client import MongoClient

from AutoRevise.course_extractor.app.config.settings import MONGODB_URI



def get_mongodb_connection():
    client = MongoClient(MONGODB_URI)
    # Send a ping to confirm a successful connection
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)
