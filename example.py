
 

# example.py
import os
import pickle
import io
import google.auth
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload
from GoogleDr_api import *


# Authenticate and get the drive_service object
drive_service = authenticate_google_drive()
folder_name = "abc123456"
folder_id = get_folder_id(drive_service, folder_name)
file_name_to_read = "abc123456.encrypted"
file_id = get_file_id_by_name(drive_service, file_name_to_read, parent_id=folder_id)


file_content = read_file2(drive_service, file_id)
print("File content:", file_content)

# # Set the local and remote file names
# local_file_name = 'upload.txt'
# # make the code can run in any directory
# script_directory = os.path.dirname(os.path.abspath(__file__))
# local_file_path = os.path.join(script_directory, local_file_name)


# # Read file content from local file
# with open(local_file_path, 'r') as f:
#     file_content = f.read()

# # Create a file in Google Drive
# file_id = create_file(drive_service, os.path.basename(local_file_path), file_content, folder_id)


#  # Change permissions for the file
# user_email = '6348projectutd2023@gmail.com'
# change_permissions(drive_service, file_id, user_email)




# # Download the file
# output_file_name = os.path.join(script_directory, 'downloaded.txt')  # Updated
# file_name_to_download = "upload.txt"
# file_id_to_download = get_file_id_by_name(drive_service, file_name_to_download, parent_id=folder_id)
# download_file(drive_service, file_id_to_download, output_file_name)




# # # Delete the file by name
# # file_name_to_delete = "upload.txt"
# # file_id_to_delete = get_file_id_by_name(drive_service, file_name_to_delete, parent_id=folder_id)
# # delete_file(drive_service, file_id_to_delete)


# folder_name = "MyNewFolder"

# # Generate read-only shareable link for the folder by name
# shareable_folder_link = generate_link_by_name(drive_service, folder_name)
# if shareable_folder_link:
#     print(f'Shareable folder link: {shareable_folder_link}')

# #example of read and rerite file

# drive_service = authenticate_google_drive()
# folder_name = "temple"
# folder_id = get_folder_id(drive_service, folder_name)
# file_name_to_read = "txs220004.encrypted"
# file_id = get_file_id_by_name(drive_service, file_name_to_read, parent_id=folder_id)

# # Read the file content
# file_content = read_file(drive_service, file_id)
# print("File content:", file_content)

# # rewrite the file content
# new_content = "it is a new hello world"
# rewrite_file(drive_service, file_id, new_content, mime_type='text/plain')
# print(read_file(drive_service, file_id))
    
