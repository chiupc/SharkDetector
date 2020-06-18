import boto3
import json
import http.client
from urllib.parse import urlencode
import logging
from datetime import datetime,timedelta
import pandas as pd
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
#Demonstrates a simple HTTP request from Lambda
    logger.debug(event)
    symbol=event['counter']
    resolution=event['resolution']
    end_time=int(datetime.now().timestamp())
    start_time=int((datetime.now() - timedelta(hours=24)).timestamp())
    logger.debug("Start time:" + str(start_time) + " End time:" + str(end_time))
    headers = {"Content-type": "application/json"}
    payload = {"symbol":symbol,"resolution":resolution,"from":start_time,"to":end_time}
    logger.debug(urlencode(payload))
    conn = http.client.HTTPSConnection("www.klsescreener.com")
    conn.request("GET", "/v2/trading_view/history", urlencode(payload), headers)
    response = conn.getresponse()
    res = json.loads(response.read()) #load data into a dict of objects, posts
    logger.debug(res)
    df = pd.read_json(res)
    df.to_csv('/tmp/temp.csv')
    # Let's get the unique userId, there should only be 1-10
    #unique_ids = set()
    #for post in posts:
    #    unique_ids.add(post['userId'])
    #logger.debug('unique_ids = {}'.format(unique_ids))
    return True