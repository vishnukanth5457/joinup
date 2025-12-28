from pymongo import MongoClient
import sys
url='mongodb://localhost:27017'
try:
    client=MongoClient(url, serverSelectionTimeoutMS=3000)
    db=client['joinup']
    names=db.list_collection_names()
    print('OK collections:', names)
except Exception as e:
    print('ERROR', e)
    sys.exit(1)
