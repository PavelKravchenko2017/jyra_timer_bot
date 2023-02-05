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

    i = 0
    sum_seconds = 0
    index_multiple = 1

    last_item_index = len(list_result[0]['TIME_ARRAY'])
    print('last_item_index: ' + str(last_item_index))

    for item in list_result[0]['TIME_ARRAY']:
        if index_multiple!=last_item_index:
            print('[' + str(index_multiple)+']' +'[' + str(i)+']' + str(list_result[0]['TIME_ARRAY'][i].timestamp()))
            if index_multiple%2==0:
                sum_seconds = sum_seconds+list_result[0]['TIME_ARRAY'][i].timestamp() - list_result[0]['TIME_ARRAY'][i-1].timestamp() 



        else:
            break
        i=i+1
        index_multiple=index_multiple + 1

    return sum_seconds
