import json, boto3

# This function will send a notification to the relative host's sqs queue to let the host know that it needs to pull an object from the S3

def lambda_handler(event, context):
    sqs = boto3.client('sqs')
    
    results = []

    try:
        jsonEvent = json.loads(event['body'], strict=False)
    # This except has to exist for testing
    except:
        jsonEvent = event
    
    s3Info = jsonEvent['Records'][0]['s3']['object']['key']
    
    # Grab the hostname
    splitKey = str(s3Info).split('/')
    if "result" in s3Info:
        queueName = splitKey[1] + '-Result'
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
    if 'notification.txt' not in s3Info:
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