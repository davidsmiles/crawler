"""
NOT USEFUL AT THE MOMENT
>> Its a script to send a file to S3 bucket
"""

import os
import boto3
from botocore.client import Config
from dotenv import load_dotenv


load_dotenv('.env')
ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
ACCESS_SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = 'smiles-scraped-data'

data = open('the-file-to-send', 'rb')
s3 = boto3.resource('s3',
                    aws_access_key_id=ACCESS_KEY_ID,
                    aws_secret_access_key=ACCESS_SECRET_KEY,
                    config=Config(signature_version='s3v4')
                    )
# #s3.Bucket(BUCKET_NAME).put_object(Key='data/ebay.csv', Body=data)
# s3.Bucket(BUCKET_NAME).put_object(Key='data/david.txt', Body=data)

s3 = boto3.client('s3')
s3.download_file(BUCKET_NAME, 'data/all_legacy_rankings.csv', 'ebay.csv')
print('Done')
