'''
Author: Vineeth Penugonda
ID: 12557722
Course: IST 6443
'''
import json
import requests
import os, sys
from urllib.parse import urlparse
from multiprocessing.pool import ThreadPool
import random
from time import time as timer

# http://api.crossref.org/works?query=%22sulphide%22&rows=1&filter=has-full-text:true,license.url:http://creativecommons.org/licenses/by/4.0/

query = "chalcogenide"
rows = 5000
filters = ["has-full-text:true", "license.url"]
licenses = list()

saveJSONLocation = "/Users/vineethpenugonda/Documents/Academics/Masters/Semester III/IST 6443/Project/virtenv/JSON/"
saveFileLocation = "/Users/vineethpenugonda/Documents/Academics/Masters/Semester III/IST 6443/Project/virtenv/Files/" + query + "/"
jsonFile = ""
totalNoOfArticlesRetrieved = 0
ftURLList = list()

def main():
    createFolder()
    fetchLicense()

    for licenseCounter in range(len(licenses)):  
        print("----------------------------------------------\n")
        urlBuilder(licenseCounter)
        noOfArticles = jsonParser()
        if noOfArticles != 0: 
            parallelDownloader()
        else:
            print("Not running downloader!")
    
    print("Total No. Of Articles Retrieved: " + totalNoOfArticlesRetrieved)
    print("----------------------------------------------")

def fetchLicense():
    global licenses
    licenseFile = open("inc/CC_licenses_urls.txt", "r")
    for license in licenseFile:
        licenses.append(license.strip('\n'))


def urlBuilder(licenseIndex = 0):
    url = "http://api.crossref.org/works?query=%s&rows=%s&filter=%s,%s:%s" % (query, rows, filters[0], filters[1], licenses[licenseIndex])

    print("License: " + licenses[licenseIndex])

    global jsonFile
    jsonFile = requests.get(url)

    fileName = licenses[licenseIndex].replace('/','_')[6:] + ".json"

    # print(fileName + "\n\n")

    open(saveJSONLocation+fileName,'wb').write(jsonFile.content)

   # print(url)

def jsonParser():
    links = list()
    global totalNoOfArticlesRetrieved
    global ftURLList
    jsonContent = json.loads(jsonFile.content)
    jsonMessage = jsonContent.get(("message"))
    jsonItem = jsonMessage.get(("items"))
    #print(jsonItem)
    for item in jsonItem or []:
        links.append(item['link'])
    #print(links)
    #print("\n\n\n\n")
    for count in range(len(links)):
        subLinks = links[count]
        # print(subLinks)
        # print("\n\n\n\n")
        for linkIndex in range(len(subLinks)):
            if (subLinks[linkIndex]['intended-application'] == "text-mining"):
                ftURL = subLinks[linkIndex]['URL']
                ftURLList.append(ftURL)
                #print(str(noOfArticles) + "\t" + ftURL)
                totalNoOfArticlesRetrieved = len(ftURLList) + totalNoOfArticlesRetrieved

    print("\nNo Of Articles Retrieved: " + str(len(ftURLList)) + "\n")
    return len(ftURLList)

def createFolder():
    if not os.path.exists(saveFileLocation):
        os.mkdir(saveFileLocation)
        print("Directory " , saveFileLocation ,  " Created ")
    else:    
        print("Directory " , saveFileLocation ,  " already exists")

def saveFile(url):
    # FILE NAME START
    urlParser = urlparse(url)
    fileName = str(random.randrange(1, 100000, 1)) + "_" + str(random.randrange(50,1000)) + "_" + os.path.basename(urlParser.path)
    # FILE NAME END

    print("Downloading: ", url)
    try:
        getContent = requests.get(url, stream=True)
        if getContent.status_code == requests.codes.ok:
            with open(saveFileLocation+fileName, 'wb') as f:
                for data in getContent:
                    f.write(data)
        return url
    except requests.exceptions.SSLError as errh:
        print("Server Problem!\n")


def parallelDownloader():
    # Download Files Parallely
    pool = ThreadPool(6)
    results = pool.map(saveFile, ftURLList)
    start = timer()
    for r in results:
        try:
            print("Downloaded: " + r)
             # #close the pool and wait for the work to finish 
            # results.close()
            # results.join()   
        except TypeError:
            print("Downloaded: Might be a server problem.\n")
    
    #close the pool and wait for the work to finish 
    pool.close()
    pool.join()    
    
    print(f"Elapsed Time: {timer() - start}" + "\n")

main()
