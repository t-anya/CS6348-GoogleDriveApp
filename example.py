# example.py

import os
from GoogleDr_api import (
    authenticate_google_drive,
    create_folder,
    create_file,
    change_permissions,
    get_file_id_by_name,
    download_file,
    delete_file,
    generate_link_by_name
)


# Authenticate and get the drive_service object
drive_service = authenticate_google_drive()



# Create a folder in Google Drive
folder_name = "MyNewFolder"
folder_id = create_folder(drive_service, folder_name)

# Set the local and remote file names
local_file_name = 'upload.txt'
# make the code can run in any directory
script_directory = os.path.dirname(os.path.abspath(__file__))
local_file_path = os.path.join(script_directory, local_file_name)


# Read file content from local file
with open(local_file_path, 'r') as f:
    file_content = f.read()

# Create a file in Google Drive
file_id = create_file(drive_service, os.path.basename(local_file_path), file_content, folder_id)


 # Change permissions for the file
user_email = '6348projectutd2023@gmail.com'
change_permissions(drive_service, file_id, user_email)




# Download the file
output_file_name = os.path.join(script_directory, 'downloaded.txt')  # Updated
file_name_to_download = "upload.txt"
file_id_to_download = get_file_id_by_name(drive_service, file_name_to_download, parent_id=folder_id)
download_file(drive_service, file_id_to_download, output_file_name)




# # Delete the file by name
# file_name_to_delete = "upload.txt"
# file_id_to_delete = get_file_id_by_name(drive_service, file_name_to_delete, parent_id=folder_id)
# delete_file(drive_service, file_id_to_delete)


folder_name = "MyNewFolder"

# Generate read-only shareable link for the folder by name
shareable_folder_link = generate_link_by_name(drive_service, folder_name)
if shareable_folder_link:
    print(f'Shareable folder link: {shareable_folder_link}')