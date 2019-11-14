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
from datetime import datetime

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
logFileName = "log_" + str(datetime.now()).replace(" ","_") + ".txt"
logFileLoc = "/Users/vineethpenugonda/Documents/Academics/Masters/Semester III/IST 6443/Project/virtenv/Logs/" + logFileName
logWriter = None

def main():
    
    # Creating a log file
    global logWriter
    logWriter = open(logFileLoc, "a+")
    print("\nLog: " + logFileName)

    print("\nQuery: " + query + "\n")
    writeLogs("\nQuery: " + query + "\n\n")
    

    createFolder()
    fetchLicense()

    # Initiating the progress bar
    printProgressBar(0, len(licenses), prefix = 'Progress:', suffix = 'Complete')

    for licenseCounter in range(len(licenses)):  
        writeLogs("\n\n----------------------------------------------\n\n")
        urlBuilder(licenseCounter)
        noOfArticles = jsonParser()
        printProgressBar(licenseCounter, len(licenses), prefix = 'Progress:', suffix = 'Complete')
        if noOfArticles != 0: 
            parallelDownloader()
        else:
            writeLogs("Not running downloader!")
            pass
    
    print("\nTotal No. Of Articles Retrieved: " + totalNoOfArticlesRetrieved)
    writeLogs("\nTotal No. Of Articles Retrieved: " + totalNoOfArticlesRetrieved)
    print("\n\nCompleted!")
    writeLogs("\n\nCompleted!")
    writeLogs("\n----------------------------------------------")



def fetchLicense():
    global licenses
    licenseFile = open("inc/CC_licenses_urls.txt", "r")
    for license in licenseFile:
        licenses.append(license.strip('\n'))
    lenOfLicenses = len(licenses)


def urlBuilder(licenseIndex = 0):
    url = "http://api.crossref.org/works?query=%s&rows=%s&filter=%s,%s:%s" % (query, rows, filters[0], filters[1], licenses[licenseIndex])

    writeLogs("License: " + licenses[licenseIndex])

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

    writeLogs("\nNo Of Articles Retrieved: " + str(len(ftURLList)) + "\n")
    return len(ftURLList)

def createFolder():
    if not os.path.exists(saveFileLocation):
        os.mkdir(saveFileLocation)
        writeLogs("Directory "  + saveFileLocation + " Created\n\n")
    else:    
        writeLogs("Directory " + saveFileLocation  + " already exist\n\n")

def saveFile(url):
    # FILE NAME START
    urlParser = urlparse(url)
    fileName = str(random.randrange(1, 100000, 1)) + "_" + str(random.randrange(50,1000)) + "_" + os.path.basename(urlParser.path)
    # FILE NAME END

    writeLogs("\nDownloading: " + url)
    try:
        getContent = requests.get(url, stream=True)
        if getContent.status_code == requests.codes.ok:
            with open(saveFileLocation+fileName, 'wb') as f:
                for data in getContent:
                    f.write(data)
        return url
    except requests.exceptions.SSLError as errh:
        writeLogs("Server Problem!\n")


def parallelDownloader():
    # Download Files Parallely
    pool = ThreadPool(12)
    results = pool.map(saveFile, ftURLList)
    start = timer()
    for r in results:
        try:
            writeLogs("\nDownloaded: " + r)
            pass 
        except TypeError:
           writeLogs("\nDownloaded: Might be a server problem.\n")
           
    
    #close the pool and wait for the work to finish 
    pool.close()
    pool.join()    
    
    #print(f"Elapsed Time: {timer() - start}" + "\n")

def writeLogs(logStr):
    logWriter.write(logStr)

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = printEnd)
    # Print New Line on Complete
    if iteration == total: 
        print()

main()
