from pymongo import MongoClient
import pymongo


def db_connect(connection_string: str, db: str, collection: str):
    try:
        # creating a client
        db_client = MongoClient(connection_string)

        # returning a connection to db so you only need to query/insert afterwards
        return db_client[db][collection]

    except:
        print('Error: db related')
        raise Exception('Error: db related')
