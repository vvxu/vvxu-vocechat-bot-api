import pymongo
from config import Settings


class PymongoCRUD:
    def __init__(self, db_name, collection_name):
        self.client = pymongo.MongoClient(Settings.Mongo['uri'])
        self.database = self.client[db_name]
        self.collection = self.database[collection_name]

    def insert_one(self, data):
        # data {name1: data1, name2: data2}
        return self.collection.insert_one(data)

    def insert_many(self, data_list):
        return self.collection.insert_many(data_list)

    def find_one(self, filter):
        return self.collection.find_one(filter)

    def find_many(self, filter):
        return self.collection.find(filter)

    def find_all(self):
        return self.collection.find()

    def update_one(self, filter, update):
        set_update = {"$set": update}
        return self.collection.update_one(filter, set_update)

    def update_many(self, filter, update):
        return self.collection.update_many(filter, update)

    def delete_one(self, filter):
        return self.collection.delete_one(filter)

    def delete_many(self, filter):
        return self.collection.delete_many(filter)

    def drop_collection(self):
        return self.collection.drop()

    def drop_database(self):
        return self.database.drop()
    