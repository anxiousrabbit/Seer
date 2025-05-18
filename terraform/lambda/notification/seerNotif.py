import json, boto3

# This function will send a notification to the relative host's sqs queue to let the host know that it needs to pull an object from the S3

def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    s3 = boto3.client('s3')
    
    results = []

    try:
        jsonEvent = json.loads(event['body'], strict=False)
    # This except has to exist for testing
    except:
        jsonEvent = event
    
    s3Info = jsonEvent['Records'][0]['s3']['object']['key']
    s3Bucket = jsonEvent['Records'][0]['s3']['bucket']['name']
    
    # Grab the hostname
    splitKey = str(s3Info).split('/')
    if "result" in s3Info:
        queueName = splitKey[1] + '-Result'

        # Get S3 metadata
        response = s3.head_object(Bucket=s3Bucket, Key=s3Info)
        metadata = response['Metadata']['action']
    else:
        queueName = splitKey[1] + '-Comped'

    # Get the queue URL
    try:
        response = sqs.get_queue_url (
            QueueName = queueName
        )
        queueUrl = response['QueueUrl']
    except Exception as error:
        print(error) 
    
    # Post the message
    if 'notification.txt' not in s3Info and 'result' in s3Info:
        try:
            response = sqs.send_message (
                QueueUrl = queueUrl,
                MessageBody = splitKey[1],
                MessageAttributes = {
                'Path' : {
                    'DataType': 'String',
                    'StringValue': s3Info
                },
                'Action' : {
                    'DataType':'String',
                    'StringValue': metadata
                }
                }
            )
        except Exception as error:
            print(error)
    else:
        try:
            response = sqs.send_message (
                QueueUrl = queueUrl,
                MessageBody = splitKey[1],
                MessageAttributes = {
                'Path' : {
                    'DataType': 'String',
                    'StringValue': s3Info
                }
                }
            )
        except Exception as error:
            print(error)