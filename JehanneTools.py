import json
import os
from pymongo import MongoClient

MONGODB_URI = os.environ.get('MONGODB_URI')


def get_status(status='all'):
    with MongoClient(MONGODB_URI) as client:
        jehanne_db = client[MONGODB_URI.split('/')[-1]]
        jehanne_status = jehanne_db['status'].find_one({'name': 'Jehanne'})
    if status == 'all':
        return jehanne_status
    else:
        return jehanne_status.get(status, None)


def set_status(status, value):
    with MongoClient(MONGODB_URI) as client:
        jehanne_db = client[MONGODB_URI.split('/')[-1]]
        jehanne_status = jehanne_db['status']
        fields = jehanne_status.find_one({'name': 'Jehanne'}).keys()
        if status in fields:
            jehanne_status.update_one({'name': 'Jehanne'}, {'$set': {status: value}})
