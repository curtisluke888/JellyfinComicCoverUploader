#To add:
#debugging mode
#   -add succesful upload message == response 204
#add ability to pass path from cli
#class implementation
#   -add api key support
#add ComicAPI Connection


import rarfile, os, requests,base64, json, zipfile
from  natsort import natsorted
from pdf2image import convert_from_path
from io import BytesIO

acceptableComicFileTypes = [".cbr", ".cbz", ".pdf"]
validImageTypes = [".jpg", ".png"]

class JellyfinInterface():
    def __init__(self, serverAddress, debug=False, client="other", device="my-script", deviceId="0000", version="0.0.0"):
        self.serverAddress = serverAddress
        self.authorization = 'MediaBrowser Client="' + client + '", Device="' + device + '", DeviceId="' + deviceId + '", Version="' + version + ' "'
        self.headers = {}
        self.debug = debug
    
    def extractCbz(self, fileName):
        with zipfile.ZipFile(fileName, "r") as comic:
            for item in natsorted(comic.namelist()):
                if('.jpg' in item.lower() or '.png' in item.lower()):
                    coverPath = item
                    break
            
            return comic.read(coverPath)
        
    def extractCbr(self, fileName):
        with rarfile.RarFile(fileName) as comic:
            coverPath=""
        
            for item in natsorted(comic.namelist()):
                if('.jpg' in item.lower() or '.png' in item.lower()):
                    coverPath = item
                    break
    
            return comic.read(coverPath)
    
    def extractPdf(self, fileName):
        cover = convert_from_path(fileName, first_page=0, last_page=1)[0]
        buffered = BytesIO()
        cover.save(buffered, format="JPEG")
        return buffered.getvalue()
    
    def extractCoverImage(self, fileName):
        if(self.debug):
            print("Attempting to extract: " + fileName)
        
        if(rarfile.is_rarfile(fileName)):
            return self.extractCbr(fileName)
        elif('.cbz' in fileName):
            return self.extractCbz(fileName)
        elif('.pdf' in fileName):
            return self.extractPdf(fileName)
        else:
            print ("ERROR: FILE IS NOT OF RECOGNIZED SUPPORT " + acceptableComicFileTypes)
        
        
        
    def setImageAPI(self, fileName):
        
        imagePayload = self.imageToBase64(self.extractCoverImage(fileName))
        
        self.headers['Content-Type'] = "image/jpeg"
        
        itemId = self.getItemId(fileName)
        
        response = requests.post(self.serverAddress + "Items/" + str(itemId) + "/Images/Primary", headers=self.headers, data=imagePayload)
            
        if(self.debug):
            if(response.status_code == 204):
                print ("POST Response: " + str(response) + "\nFile: " + fileName + "'s image has been uploaded")
            else:
                print ("POST Response: " + str(response) + "\nFile: " + fileName + "'s image has failed POST request")
            print (response.url)
        
        self.headers.pop('Content-Type')
        
        if(self.debug):
            with open('responseSetImage.json', 'wb') as outstream:
                outstream.write(response.content)
            
    def imageToBase64(self, image):
        return base64.b64encode(image).decode('utf-8')
            
    def start(self, startDirectory = os.getcwd()):
        print ("Program has started.")
        for comicFile in os.listdir(startDirectory):
            if(os.path.isdir(os.path.join(startDirectory,comicFile))):
                    self.start(os.path.join(startDirectory,comicFile))
                    continue
            if(os.path.splitext(comicFile)[1] in acceptableComicFileTypes):
                try:
                    self.setImageAPI(os.path.join(startDirectory,comicFile))
                except:
                    print (os.path.join(startDirectory,comicFile) + " has failed to upload." )
        print ("Program has completed.")
                
                
    #make this method called _fast; it only returns if jellyfin title is same as file path
    def getItemId(self, fileName):
        
        searchTerm = os.path.basename(fileName.split(".",1)[0])
        
        response = requests.get(self.serverAddress + "Users/" + self.user_id + "/Items?recursive=true&fields=path&searchTerm=" + searchTerm, headers=self.headers)
        if(self.debug):
            print ("Search Term : " + searchTerm)
            print ("GET Item Id Response: " + str(response))
            print ("URL: " + response.url)
            with open('responseItemId.json', 'wb') as outstream:
                outstream.write(response.content)
        if (response.json().get('Items') == []):
            print ("getItemId has returned no results. Either the file is not loaded onto JellyFin or the comic file name is to generic.")
            return -1
        
        itemId = 0
        
        for responseItems in response.json().get('Items'):
            if (responseItems.get('Path') == os.path.abspath(fileName)):
                itemId = responseItems.get('Id')
        
        return itemId
        
    def loginPassword(self, username, password):
        payload = {"Username": username, "Pw": password}
     
        self.headers['Authorization'] = self.authorization
        
        response = requests.post(self.serverAddress + "Users/AuthenticateByName", headers=self.headers, json=payload)
        
        self.token = response.json().get('AccessToken')
        self.user_id = response.json().get('User').get('Id')
        self.headers['Authorization'] = f'{self.authorization}, Token="{self.token}"'
        if(self.debug):
            print ("Login Response: " + str(response))
            with open('responseLoginPassword.json', 'wb') as outstream:
                outstream.write(response.content)
