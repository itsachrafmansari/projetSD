from pymongo import MongoClient, errors


class AtlasClient:
    def __init__(self, altas_uri: str, dbname: str):
        self.mongodb_client = MongoClient(altas_uri)
        self.database = self.mongodb_client[dbname]

    def ping(self):
        return self.mongodb_client.admin.command('ping')

    def get_collection(self, collection_name: str):
        return self.database[collection_name]

    def create_collection(self, collection_name: str):
        return self.database[collection_name]

    def get_items_from(self, collection_name: str, filters: dict = None, limit: int = 0):
        collection = self.database[collection_name]
        items = list(collection.find(filter=filters, limit=limit))
        return items

    def insert_many(self, collection_name: str, items: list):
        collection = self.database[collection_name]
        collection.insert_many(items, ordered=False)
