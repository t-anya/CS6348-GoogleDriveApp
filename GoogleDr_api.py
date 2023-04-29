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





def authenticate_google_drive():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/drive']
    CLIENT_SECRET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client_secret.json')

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8080)
        
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    try:
        drive_service = build('drive', 'v3', credentials=creds)
        return drive_service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def create_folder(drive_service, folder_name, parent_id=None):
    folder_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    
    if parent_id:
        folder_metadata['parents'] = [parent_id]
    
    folder = drive_service.files().create(body=folder_metadata, fields='id').execute()
    print(f"Folder ID: '{folder.get('id')}'.")

    return folder.get('id')



import tempfile
def create_file(drive_service, file_name, file_content, parent_id=None, mime_type='text/plain'):
    file_metadata = {'name': file_name}
    if parent_id:
        file_metadata['parents'] = [parent_id]

    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file.flush()

        media = MediaFileUpload(temp_file.name, mimetype=mime_type)
        file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    os.unlink(temp_file.name)  # remove the temporary file
    print(f'File ID: "{file.get("id")}".')
    return file.get("id")


def get_folder_id(drive_service, folder_name):
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    if not items:
        print(f"No folder found with name: {folder_name}")
        return None
    else:
        folder_id = items[0]["id"]
        print(f"Found folder with name '{folder_name}' and ID '{folder_id}'")
        return folder_id
    
def download_file(drive_service, file_id, output_file_name):
    request = drive_service.files().get_media(fileId=file_id)
    file = io.BytesIO()
    downloader = MediaIoBaseDownload(file, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))

    file.seek(0)
    with open(output_file_name, 'wb') as f:
        f.write(file.read())
    print(f'The file has been downloaded to {output_file_name}')

def change_permissions(drive_service, file_id, user_email, role='writer', type='user'):
    try:
        permission = {'type': type, 'role': role, 'emailAddress': user_email}
        drive_service.permissions().create(fileId=file_id, body=permission, fields='id').execute()
        print(f'Permission has been granted to {user_email} with {role} access.')
    except HttpError as error:
        print(f'An error occurred: {error}')
        
        
def get_file_id_by_name(drive_service, file_name, parent_id=None):
    query = f"name='{file_name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    results = drive_service.files().list(q=query, fields="nextPageToken, files(id, name)").execute()
    items = results.get("files", [])
    if not items:
        print(f"No file found with name: {file_name}")
        return None
    else:
        file_id = items[0]["id"]
        print(f"Found file with name '{file_name}' and ID '{file_id}'")
        return file_id
    

def delete_file(drive_service, file_id):
    try:
        drive_service.files().delete(fileId=file_id).execute()
        print(f'File with ID "{file_id}" has been deleted.')
    except HttpError as error:
        print(f'An error occurred: {error}')
        
if __name__ == '__main__':
    '''
    # Authenticate and get the drive_service object
    drive_service = authenticate_google_drive()
    
 

    # Create a folder in Google Drive
    folder_name = "MyNewFolder"
    folder_id = create_folder(drive_service, folder_name)

    # Set the local and remote file names
    local_file_name = 'upload.txt'
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
    output_file_name = 'downloaded.txt'
    file_name_to_download = "upload.txt"
    file_id_to_download = get_file_id_by_name(drive_service, file_name_to_download, parent_id=folder_id)
    download_file(drive_service, file_id_to_download, output_file_name)
    
    

    # Delete the file by name
    file_name_to_delete = "upload.txt"
    file_id_to_delete = get_file_id_by_name(drive_service, file_name_to_delete, parent_id=folder_id)
    delete_file(drive_service, file_id_to_delete)
    '''
