import pymongo

import time
import logging
import asyncio

client = pymongo.MongoClient('localhost', 27017)
database = client['TASK_MANAGER_DB']


def calculate_value_in_TIME_ARRAY(TASK_ID):
    print('calculate_value_in_TIME_ARRAY__start')   #TIME_ARRAY
  
    
    result = database['TASK_LIST'].find({ 'TASK_ID': TASK_ID})

    buf_cursor = result.clone()
    list_result = list(buf_cursor)

    print('list_result:')

    i = 1
    for item in list_result[0]['TIME_ARRAY']:
        print('[' + str(i)+']' + str(item))
        i=i+1

    return 666
