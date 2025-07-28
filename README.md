# JellyfinComicCoverUploader
Uploads comic covers as primary image using API
Note: also works with regular books as well

## Compatible FIle Types: ## 
* cbz
* cbr
* pdf


## Requirements: ## 

- Comic file names are very much encouraged be unique.(No, "Issue #1", or "#1", etc. Instead "Radiant Black (2021) Issue#1"). THis is to make sure the wrong file doesn't get uploaded.

- Must install Poppler in order for pdf2image to work

- Must have One of the backends from https://pypi.org/project/rarfile/ page installed for rarfile to work

- Install libraries with 'pip install -r requirements.txt'


## Uses: ## 
This program/script is meant to be ran in a folder that contains all the comic files that are in a JellyFin server. 
This program is meant to be run offline and uses the data stored within the file. It also requires a Username and Password (and in the future potentially an api key) to authenticate the user.

To start try something like this:

`from comic_cover_getter.py import JellyfinInterface
server = JellyfinInterface("http://127.0.0.0/")`

Replace "http://127.0.0.0/" with your server name. But keep the ending slash.
This creates the class that will store your address and login info.

To Login use something like this

`server.loginPassword("Username", "Password")`

Replace "Username" and "Password" with your actual username and password for the jellyfin server. 

Then (if the login was successful) to start the process:

`server.start()`

You can also use

`server.start(startDirectory="path\to\comic_foler\")`

Where "path\to\comic_foler\" is your desired starting path
