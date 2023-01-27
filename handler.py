from datetime import datetime
from distutils.command.upload import upload
from urllib import response
import boto3
from io import BytesIO
from PIL import Image, ImageOps
import os
import uuid
import json

s3 = boto3.client('s3')
size = int(os.environ['THUMBNAIL_SIZE'])

def s3_thumbnail_generator(event, context):
    print("EVENT:", event)
    print("CONTEXT:", context)

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    image_size = event['Records'][0]['s3']['object']['size']

    if (not key.endswith('_thumbnail.png')):
        image = get_s3_image(bucket, key)
        thumbnail = image_to_thumbnail(image)
        thumbnail_key = new_filename(key)
        url = upload_to_s3(bucket, thumbnail_key, thumbnail, image_size)

        return url

def get_s3_image(bucket, key):
    response = s3.get_object(Bucket=bucket, Key=key)
    image_content = response['Body'].read()

    file = BytesIO(image_content)
    image = Image.open(file)

    return image

def image_to_thumbnail(image):
    return ImageOps.fit(image, (size, size), Image.ANTIALIAS)

def new_filename(key):
    key_split = key.rsplit('.', 1)
    return key_split[0] + "_thumbnail.png"

def upload_to_s3(bucket, key, image, image_size):
    out_thumbnail = BytesIO()

    image.save(out_thumbnail, 'PNG')
    out_thumbnail.seek(0)

    response = s3.put_object(
      ACL='public-read',
      Body=out_thumbnail,
      Bucket=bucket,
      ContentType='image/png',
      Key=key
    )
    print('UPLOAD RESPONSE:', response)

    url = '{}/{}/{}'.format(s3.meta.endpoint_url, bucket, key)

    return url
