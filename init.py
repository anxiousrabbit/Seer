import cloud
import os
import json
import keyring
import getpass

# Initialize the program
class initFile:
    def __init__(self):
        self.imgDir = ''
        self.resultDir = ''
        self.fileName = 'init.json'
        self.initResult = False
        self.credStore = 'None'
        self.dalleKey = 'None'
        self.fileUpload = False
        self.directoryUpload = cloud.bucketFunctions()
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