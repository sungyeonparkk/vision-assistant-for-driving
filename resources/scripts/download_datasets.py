import argparse
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from tqdm import tqdm

try:
    with open('/mount/credentials.json', 'r') as f:
        with open('credentials.json', 'w') as f2:
            f2.write(f.read())
except Exception as e:
    print(e)
    pass

gauth = GoogleAuth()
gauth.LoadCredentialsFile(os.path.realpath("credentials.json"))
# gauth.LoadCredentialsFile(os.path.realpath("./credentials.json"))
(gauth.Authorize() if not gauth.access_token_expired else gauth.Refresh()) \
    if gauth.credentials else gauth.CommandLineAuth()
drive = GoogleDrive(gauth)


def is_folder(file):
    return 'folder' in file['mimeType']


def download(file, root_dir, dry_run):
    if not dry_run:
        path = os.path.join(root_dir, file['title'])
        path = os.path.join('/input', path)
        directory = os.path.dirname(path)
        os.makedirs(directory, exist_ok=True)
        drive.CreateFile({'id': file['id']}).GetContentFile(path)
    else:
        print('Dry run, skipping download... {}'.format(file['title']))


def download_folder(dataset_folder_id, root_dir: str, dry_run: bool):
    file_list = drive.ListFile({'q': "'{}' in parents and trashed=false".format(dataset_folder_id)}).GetList()

    if len(file_list) == 0:
        print('No files found For {}. Exiting...'.format(root_dir))
        return

    folders = []
    for file in tqdm(file_list):

        if is_folder(file):
            print('Found Folder Path: %s, ID: %s' % (os.path.join(root_dir, file['title']), file['id']))
            folders.append(file)
            continue

        print('Found File Path: %s, ID: %s' % (os.path.join(root_dir, file['title']), file['id']))
        download(file, root_dir, dry_run)

    if len(folders) > 0:
        for folder in folders:
            download_folder(folder['id'], os.path.join(root_dir, folder['title']), dry_run)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root_folder_id', type=str, required=False)
    parser.add_argument('--dry_run', type=bool, required=False, default=False)
    args = parser.parse_args()
    # 1chA5Iv85efLInPYpFMLyZWWH5MIy36aI
    if not args.root_folder_id:
        args.root_folder_id = input('Enter the root folder id: ')

    root_folder = drive.CreateFile({'id': args.root_folder_id})

    if not is_folder(root_folder):
        print('Downloading File {}'.format(root_folder['title']))
        download(root_folder, '', args.dry_run)
    else:
        print('Downloading files from folder: {} with id: {}'.format(root_folder['title'], args.root_folder_id))
        download_folder(args.root_folder_id, root_folder['title'], args.dry_run)
