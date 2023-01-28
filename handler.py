from datetime import datetime
from distutils.command.upload import upload
from urllib import response
import boto3
from io import BytesIO
from PIL import Image, ImageOps
import os
import uuid
import json

size = int(os.environ['THUMBNAIL_SIZE'])
db_table = str(os.environ['DYNAMODB_TABLE'])
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb', region_name=str(os.environ['REGION_NAME']))

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
        response = s3_save_thumbnail_url_to_dynamodb(url, image_size)

        return response

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

def s3_save_thumbnail_url_to_dynamodb(url_path, image_size):
    toint = float(image_size * 0.53) / 1000
    table = dynamodb.Table(db_table)
    response = table.put_item(
        Item={
          'id': str(uuid.uuid4()),
          'url': str(url_path),
          'approxReducedSize': str(toint) + str(' KB'),
          'createdAt': str(datetime.now()),
          'updatedAt': str(datetime.now())
        }
    )

    return {
      'statusCode': 200,
      'headers': {
        'Content-Type': 'application/json'
      },
      'body': json.dumps(response)
    }

def s3_get_thumbnails_urls(event, context):
  table = dynamodb.Table(db_table)
  response = table.scan()
  data = response['Items']

  while 'LastEvaluatedKey' in response:
    response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
    data.extends(response['Items'])

  return {
    'statusCode': 200,
    'headers': {
      'Content-Type': 'applications/json'
    },
    'body': json.dumps(data)
  }

def s3_get_item(event, context):
  table = dynamodb.Table(db_table)
  response = table.get_item(Key={
    'id': event['pathParameters']['id']
  })

  item = response['Item']

  return {
    'statusCode': 200,
    'headers': {
      'Content-Type': 'application/json'
    },
    'body': json.dumps(item)
  }

def s3_delete_item(event, context):
  item_id = event['pathParameters']['id']
  table = dynamodb.Table(db_table)
  delete_item_response = table.delete_item(Key={
    'id': item_id
  })

  if (delete_item_response['ResponseMetadata']['HTTPStatusCode'] == 200):
    return {
      'statusCode': 200,
      'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      'body': json.dumps({
        'deleted': True,
        'deletedItemId': item_id
      })
    }

  return {
    'statusCode': 500,
    'body': f'An error occurred while deleting post {item_id}'
  }