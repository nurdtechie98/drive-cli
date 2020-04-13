from __future__ import print_function
import os
import sys
import io
import re
import click
import json
import time
from mimetypes import MimeTypes
from pathlib import Path
from pick import Picker
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from httplib2 import Http
from oauth2client import file

dirpath = os.path.dirname(os.path.realpath(__file__))
mime = MimeTypes()


class Drive:

    def __init__(self):
        self.config_path = Path.home().joinpath(".config", "drive-cli")
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.hist_path = self.config_path.joinpath(".history")
        self.hist_path.mkdir(exist_ok=True)
        self.dclipath = self.config_path.joinpath(".dclipath")
        self.dclipath.mkdir(exist_ok=True)
        token = self.config_path.joinpath('token.json')
        if not token.is_file():
            print("This application has not been authorized. Please run 'drive login', "
                  "use 'drive login --help' for further assistance.")
            sys.exit(1)
        store = file.Storage(str(token))
        creds = store.get()
        self.service = build('drive', 'v3', http=creds.authorize(Http()))

    def get_history(self):
        if not self.hist_path.exists():
            with self.hist_path.open('w')as outfile:
                history = {}
                json.dump(history, outfile)
        else:
            with self.hist_path.open('r') as infile:
                history = json.load(infile)
        return history

    def save_history(self, info):
        date_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S").split(" ")
        date = date_time[0]
        time = date_time[1]
        command = sys.argv
        log = {"cwd": info[2],
               "command": "drive " + command[1],
               "arg": info[1],
               "flags": info[0]
               }
        history = self.get_history()
        if date not in history:
            history[date] = {}
        history[date][time] = log
        with self.hist_path.open("w") as outfile:
            json.dump(history, outfile)

    def clear_history(self):
        os.remove(str(self.hist_path))

    def drive_data(self, *argv):
        if not self.dclipath.is_file():
            with self.dclipath.open("w") as outfile:
                if (not len(argv)):
                    data = {}
                else:
                    data = argv[0]
                json.dump(data, outfile)
        else:
            if (not len(argv)):
                with self.dclipath.open("r") as infile:
                    data = json.load(infile)
            else:
                with self.dclipath.open("w") as outfile:
                    data = argv[0]
                    json.dump(data, outfile)
        return data

    @staticmethod
    def get_request(service, fid, mimeType):
        if (re.match('^application/vnd\.google-apps\..+', mimeType)):
            if (mimeType == 'application/vnd.google-apps.document'):
                mimeTypes = {extension: mime.guess_type("placeholder_filename." + extension)[0] for extension
                             in ("pdf",
                                 "txt",
                                 "doc",
                                 "zip",
                                 "html",
                                 "rtf",
                                 "odt")}
            elif (mimeType == 'application/vnd.google-apps.spreadsheet'):
                mimeTypes = {extension: mime.guess_type("placeholder_filename." + extension)[0] for extension
                             in ("pdf",
                                 "xlsx",
                                 "zip",
                                 "html",
                                 "ods",
                                 "csv",
                                 "tsv")}
            elif (mimeType == 'application/vnd.google-apps.presentation'):
                mimeTypes = {extension: mime.guess_type("paceholder_filename." + extension)[0] for extension
                             in ("pdf",
                                 "zip",
                                 "html",
                                 "pptx",
                                 "txt")}
            else:
                mimeTypes = {extension: mime.guess_type("paceholder_filename." + extension)[0] for extension
                             in ("ods",
                                 "csv",
                                 "pdf",
                                 "jpg",
                                 "png",
                                 "gif",
                                 "bmp",
                                 "txt",
                                 "doc",
                                 "js",
                                 "swf",
                                 "mp3",
                                 "zip",
                                 "rar",
                                 "tar",
                                 "cab",
                                 "html",
                                 "htm")}
                mimeTypes.update(
                    {'tmpl': 'text/plain', 'php': 'application/x-httpd-php', 'arj': 'application/arj'})
            promptMessage = 'Choose type to export to \n(ENTER to select, s to stop):'
            title = promptMessage
            options = [x for x in mimeTypes.keys()]
            picker = Picker(options, title, indicator='=>', default_index=0)
            picker.register_custom_handler(ord('s'), go_back)
            chosen, index = picker.start()
            if index != -1:
                request = service.files().export_media(
                    fileId=fid, mimeType=mimeTypes[chosen])
                return request, str("." + chosen)
            else:
                sys.exit(0)
        else:
            request = service.files().get_media(fileId=fid)
            return request, ""

    def write_needed(self, dir_name, item):
        drive_time = time.mktime(time.strptime(
            item['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ')) + float(19800.00)
        local_time = os.path.getmtime(dir_name)
        data = self.drive_data()
        sync_time = data[dir_name]['time']
        if (sync_time < drive_time):
            if (sync_time < local_time):
                input = ''
                while (input != 's' and input != 'o'):
                    input = click.prompt("Conflict: both local and online copy of " +
                                         dir_name + " has been modified\npress o to OVERWRITE s to SKIP")
                if (input == 'o'):
                    return True
            else:
                return True
        return False

    def push_needed(self, drive, item_path):
        drive_time = time.mktime(time.strptime(
            drive['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ')) + float(19800.00)
        local_time = os.path.getmtime(item_path) - float(19801.00)
        data = self.drive_data()
        sync_time = data[item_path]['time']
        if sync_time < local_time:
            if sync_time < drive_time:
                input = ''
                while (input != 's' and input != 'o'):
                    input = click.prompt("Conflict: both local and online copy of " +
                                         "dir_name" + " has been modified\npress o to OVERWRITE s to SKIP")
                    # TODO Figure out what dir_name is supposed to be
                if (input == 'o'):
                    return True
            else:
                return True
        return False

    def modified_or_created(self, sync_time, item_path):
        mtime = os.path.getmtime(item_path)
        data = self.drive_data()
        if item_path not in data.keys():
            click.secho("created: " + item_path, fg='green')
            return 1
        elif (mtime > (sync_time + 1.000)):
            click.secho("changed: " + item_path, fg='blue')
            return 1
        return 0

    @staticmethod
    def get_fid(inp):
        if 'google' in inp:
            if 'open' in inp:
                fid = inp.split('=')[-1]
            elif 'folders' in inp:
                fid = inp.split('/')[-1]
                if '?' in fid:
                    fid = fid.split('?')[-2]
            else:
                fid = inp.split('/')[-2]
        else:
            fid = inp
        return fid

    def create_new(self, cwd, fid):
        if not os.path.exists(cwd):
            os.mkdir(cwd)
        else:
            click.secho(
                'file ' + cwd + ' already exists! remove the existing file and retry', fg='red')
            sys.exit(0)
        data = self.drive_data()
        data[cwd] = {}
        data[cwd]['id'] = fid
        data[cwd]['time'] = time.time()
        self.drive_data(data)

    def delete_file(self, fid):
        fid = fid['id']
        try:
            self.service.files().delete(fileId=fid).execute()
        except:
            click.secho(
                "Error Ocurred:\n make sure that you have appropriate access", fg='red')

    def get_file(self, fid):
        files = self.service.files().get(fileId=fid).execute()
        return files

    def get_child(self, cwd):
        data = self.drive_data()
        page_token = None
        drive_lis = {}
        query = "'" + data[cwd]['id'] + "' in parents"
        while True:
            children = self.service.files().list(q=query,
                                                 spaces='drive',
                                                 fields='nextPageToken, files(id,mimeType,name,modifiedTime)',
                                                 pageToken=page_token
                                                 ).execute()
            for child in children.get('files', []):
                drive_lis[child['name']] = child
            page_token = children.get('nextPageToken', None)
            if page_token is None:
                break
        return drive_lis

    def get_child_id(self, pid, item):
        page_token = None
        query = "name = '{}' and '{}' in parents".format(item, pid)
        response = self.service.files().list(q=query,
                                             spaces='drive',
                                             fields='nextPageToken, files(id, name)',
                                             pageToken=page_token).execute()
        fils = response.get('files', [])[0]
        return fils.get('id')

    def create_dir(self, cwd, pid, name):
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [pid]
        }
        fid = self.service.files().create(body=file_metadata, fields='id').execute()
        fid['time'] = time.time()
        full_path = os.path.join(cwd, name)
        data = self.drive_data()
        data[full_path] = fid
        self.drive_data(data)
        click.secho("Created a tracked directory", fg='magenta')
        return full_path, fid['id']

    def file_download(self, item, cwd, clone=False):
        fid = item['id']
        fname = item['name']
        fh = io.BytesIO()
        click.echo("Preparing: " + click.style(fname, fg='red') + " for download")
        request, ext = self.get_request(self.service, fid, item['mimeType'])
        file_path = (os.path.join(cwd, fname) + ext)
        if (not clone and (os.path.exists(file_path)) and (not self.write_needed(file_path, item))):
            return
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        with click.progressbar(length=100, label='downloading file') as bar:
            pstatus = 0
            while done is False:
                status, done = downloader.next_chunk()
                status = int(status.progress() * 100)
                bar.update(int(status - pstatus))
                pstatus = status
            with open(file_path, 'wb') as f:
                f.write(fh.getvalue())
        data = self.drive_data()
        data[file_path] = {'id': item['id'], 'time': time.time()}
        self.drive_data(data)
        click.secho("completed download of " + fname, fg='yellow')

    def concat(self, fid):
        fh = io.BytesIO()
        item = self.get_file(fid)
        request, ext = self.get_request(self.service, fid, item['mimeType'])
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        print(fh.getvalue().decode('utf-8'))

    def upload_file(self, name, path, pid):
        file_mimeType = identify_mimetype(name)
        file_metadata = {
            'name': name,
            'parents': [pid],
            'mimeType': file_mimeType
        }
        media = MediaFileUpload(path, mimetype=file_mimeType)
        new_file = self.service.files().create(body=file_metadata,
                                               media_body=media,
                                               fields='id').execute()
        data = self.drive_data()
        data[path] = {'id': new_file['id'], 'time': time.time()}
        self.drive_data(data)
        click.secho("uploaded " + name, fg='yellow')
        return new_file

    def update_file(self, name, path, fid):
        file_mimeType = identify_mimetype(name)
        media = MediaFileUpload(path, mimetype=file_mimeType)
        new_file = self.service.files().update(fileId=fid,
                                               media_body=media,
                                               fields='id').execute()
        data = self.drive_data()
        data[path]['time'] = {'time': time.time()}
        self.drive_data(data)
        return new_file

    def pull_content(self, cwd, fid):
        data = self.drive_data()
        page_token = None
        lis = []
        query = "'" + data[cwd]['id'] + "' in parents"
        while True:
            children = self.service.files().list(q=query,
                                                 spaces='drive',
                                                 fields='nextPageToken, files(id,mimeType,name,modifiedTime)',
                                                 pageToken=page_token
                                                 ).execute()
            for child in children.get('files', []):
                lis.append(child)
            page_token = children.get('nextPageToken', None)
            if page_token is None:
                break
        for item in lis:
            dir_name = os.path.join(cwd, item['name'])
            if (item['mimeType'] != 'application/vnd.google-apps.folder'):
                if ((not os.path.exists(dir_name)) or self.write_needed(dir_name, item)):
                    self.file_download(item, cwd, data[cwd]['time'])
            else:
                if (not os.path.exists(dir_name)):
                    click.secho("creating: " + dir_name)
                    os.mkdir(dir_name)
                    data = self.drive_data()
                    data[dir_name] = {'id': item['id'], 'time': time.time()}
                    data = self.drive_data(data)
                else:
                    click.secho("updating: " + dir_name)
                self.pull_content(dir_name, item['id'])
        data = self.drive_data()
        data[cwd]['time'] = time.time()
        data = self.drive_data(data)
        self.drive_data(data)

    def list_status(self, cwd, sync_time):
        local_lis = list_local(cwd)
        changes = 0
        for item in local_lis:
            item_path = os.path.join(cwd, item)
            if (os.path.isdir(item_path)):
                if (self.modified_or_created(sync_time, item_path)):
                    changes += 1
                    data = self.drive_data()
                    if item in data.keys():
                        sync_time = data[item]
                    else:
                        sync_time = float(0)
                    self.list_status(item_path, sync_time)
            else:
                changes += self.modified_or_created(sync_time, item_path)
        if changes == 0:
            click.secho("No changes made since the last sync")

    def push_content(self, cwd, fid):
        drive_lis = self.get_child(cwd)
        local_lis = list_local(cwd)
        data = self.drive_data()
        for item in local_lis:
            item_path = os.path.join(cwd, item)
            if (os.path.isdir(item_path)):
                if item not in drive_lis.keys():
                    child_cwd, child_id = self.create_dir(cwd, fid, item)
                else:
                    child_cwd = os.path.join(cwd, item)
                    child_id = drive_lis[item]['id']
                    if child_cwd not in data.keys():
                        data[child_cwd] = {'id': child_id, 'time': time.time()}
                        data = self.drive_data(data)
                self.push_content(child_cwd, child_id)
            else:
                item_path = os.path.join(cwd, item)
                if item not in drive_lis.keys():
                    click.secho("uploading " + item + " ....")
                    self.upload_file(item, item_path, fid)
                else:
                    if (self.push_needed(drive_lis[item], item_path)):
                        click.secho("updating " + item)
                        cid = self.get_child_id(fid, item)
                        self.update_file(item, item_path, cid)
                        click.secho("updating of " + item +
                                    " completed", fg='yellow')
        data = self.drive_data()
        data[cwd]['time'] = time.time()
        self.drive_data(data)


def go_back(picker):
    return None, -1


def identify_mimetype(name):
    mimetype = mime.guess_type(name)[0]
    if mimetype is not None:
        return mimetype
    else:
        return 'application/octet-stream'


def list_local(cwd):
    local_lis = os.listdir(cwd)
    drive_ignore_path = os.path.join(cwd, '.driveignore')
    if os.path.isfile(drive_ignore_path):
        file = open(drive_ignore_path, 'r')
        untracked_files = file.readlines()
        for f in untracked_files:
            local_lis.remove(f[:-1])
        file.close()
    return local_lis
