# Python program to bulk download blob files from azure storage
# Uses latest python SDK() for Azure blob storage
# Requires python 3.6 or above
# Original version from https://www.quickprogrammingtips.com/azure/how-to-download-blobs-from-azure-storage-using-python.html
# Modified for SANS FOR509

# Requires the Azure python SDK
# pip3 install azure-storage-blob --user

import os
from multiprocessing.pool import ThreadPool
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.blob import ContentSettings, ContainerClient
from datetime import date
from os import path
 
# IMPORTANT: Replace connection string with your storage account connection string
# Usually starts with DefaultEndpointsProtocol=https;...
#
# Sample connection string
# MY_CONNECTION_STRING = "DefaultEndpointsProtocol=https;AccountName=pymtechlabslogstorage;AccountKey=og5lhNt9+ZE08/R9OvyliaA2ruX00q1Znavwy5VN<redacted>;EndpointSuffix=core.windows.net"
MY_CONNECTION_STRING = 

# IMPORTANT: You must specify a blob container
# Blob containers from the SANS FOR509 class:
#MY_BLOB_CONTAINER = "insights-logs-networksecuritygroupflowevent"
#MY_BLOB_CONTAINER = "insights-logs-auditlogs"
#MY_BLOB_CONTAINER = "insights-logs-managedidentitysigninlogs"
#MY_BLOB_CONTAINER = "insights-logs-noninteractiveusersigninlogs"
#MY_BLOB_CONTAINER = "insights-logs-serviceprincipalsigninlogs"
#MY_BLOB_CONTAINER = "insights-logs-signinlogs"
#MY_BLOB_CONTAINER = "insights-activity-logs"
#MY_BLOB_CONTAINER = "insights-logs-storageread"
MY_BLOB_CONTAINER =


today = date.today()
d1 = today.strftime('%Y%m%d')
   
# Replace with the local folder where you want files to be downloaded
# By default the script will create a directory with the date and the name of the blob container
LOCAL_BLOB_PATH = path.join('/home/elk_user/blob',d1,MY_BLOB_CONTAINER)
    
class AzureBlobFileDownloader:
  def __init__(self):
    print("Intializing AzureBlobFileDownloader")
           
    # Initialize the connection to Azure storage account
    self.blob_service_client =  BlobServiceClient.from_connection_string(MY_CONNECTION_STRING)
    self.my_container = self.blob_service_client.get_container_client(MY_BLOB_CONTAINER)
                        
                         
  def download_all_blobs_in_container(self):
    # get a list of blobs
    my_blobs = self.my_container.list_blobs()
    result = self.run(my_blobs)
    print(result)
                 
  def run(self,blobs):
    # Download 10 files at a time!
    with ThreadPool(processes=int(10)) as pool:
      return pool.map(self.save_blob_locally, blobs)
                                 
  def save_blob_locally(self,blob):
    file_name = blob.name
    print(file_name)
    bytes = self.my_container.get_blob_client(blob).download_blob().readall()
                                                
    # Get full path to the file
    download_file_path = os.path.join(LOCAL_BLOB_PATH, file_name)
    # for nested blobs, create local path as well!
    os.makedirs(os.path.dirname(download_file_path), exist_ok=True)
                                    
    with open(download_file_path, "wb") as file:
      file.write(bytes)
    return file_name


# Initialize class and upload files
azure_blob_file_downloader = AzureBlobFileDownloader()
azure_blob_file_downloader.download_all_blobs_in_container()
