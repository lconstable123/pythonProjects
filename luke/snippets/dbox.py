import dropbox
import posixpath
from dropbox.exceptions import ApiError
import os



dbpath = ""
uploadpath =""


def process_folder_entries(current_state, entries):
    count = 0
    for entry in entries:
        if isinstance(entry, dropbox.files.FileMetadata):
            count = count+1
            current_state[entry.path_lower] = entry
        elif isinstance(entry, dropbox.files.DeletedMetadata):
            current_state.pop(entry.path_lower, None) # ignore KeyError if missing
    return current_state

def path_exists(path):
    try:
        dbx.files_get_metadata(path)
        return True
    except ApiError as e:
        if e.error.get_path().is_not_found():
            return False
        raise

def checkLocalDir(localpath):
    entries = os.listdir(localpath)
    #for entry in entries:
       # print(entry)
    count = len(entries)
    print("found",count," local files")
    return count

def checkRemoteDir(remotepath):
    #print("Scanning files...")
    result = dbx.files_list_folder(path=remotepath)
    files = process_folder_entries({}, result.entries)
    
    while result.has_more:
        print(("collecting more files"))
        result = dbx.files_list_folder_continue(results.cursor)
        files = process_folder_entries(files, result.entries)

    count = len(files)
    print("found",count," remote files")
    return count
    

def upload_file(local_file_path,dropbox_file_path):
    print("trying to upload",local_file_path)
    try:
        with open(local_file_path, 'rb') as f:
            
            dbx.files_upload(f.read(),dropbox_file_path, mute=True)
            print(f"Uploaded {local_file_path} to {dropbox_file_path}")
    except:
        print("didn't work sorry, check your path syntax")

def upload_folder(local_folder_path, dropbox_folder_path):
    # Loop through all files in the local folder
    for root, dirs, files in os.walk(local_folder_path):
        # For each file in the folder, upload it
        for file in files:
            local_file_path = os.path.join(root, file)
            
            # Calculate the corresponding Dropbox path
            # This strips the base local folder path and adds it to the target Dropbox folder path
            relative_path = os.path.relpath(local_file_path, local_folder_path)
            dropbox_file_path = os.path.join(dropbox_folder_path, relative_path).replace("\\", "/")
            
            # Upload the file
            upload_file(local_file_path, dropbox_file_path)
    print("uploading folder complete")
    print("\ncomparing")
    if checkLocalDir(local_folder_path) == checkRemoteDir(dropbox_folder_path):
        print("all files uploaded")
    else:
        print("some files have been missed")
        

########


    




key = input("set dropbox key or leave blank to use default")
dbpath = input("set dropbox folder:")
uploadpath = input("set upload folder or leave blank to use local upload folder:")

if key == "":
    key = defaultkey

if dbpath =="":
    dbpath ="/foldertest2/"
    
if uploadpath == "":
    uploadpath ="upload"
    
print("initializing dropbox API...")
dbx = dropbox.Dropbox(key)

#checkDir()

upload_folder(uploadpath,dbpath)




