import os
import sys
import click
from pick import Picker
from httplib2 import Http
from oauth2client import file
from prettytable import PrettyTable
from googleapiclient.discovery import build

dirpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirpath)
import utils

@click.command('view-files', short_help='filter search files and file ID for files user has access to')
@click.option('--name', is_flag=bool, help='provide username in whose repos are to be listed.')
@click.option('--types', is_flag=bool, help='provide username in whose repos are to be listed.')
@click.option('--pid', is_flag=bool, help='provide parent file ID or sharing link and list its child file/folders.')
def view_file(name, types, pid):
    """
    view-files: Filter based list of the names and ids of the first 10 files the user has access to
    """
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    query = ""
    if name:
        q_name = click.prompt('enter the search value')
        query = "name contains '" + q_name + "' "
    if types:
        mimeTypes = {
            "xls": 'application/vnd.ms-excel',
            "xlsx": 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            "xml": 'text/xml',
            "ods": 'application/vnd.oasis.opendocument.spreadsheet',
            "csv": 'text/plain',
            "tmpl": 'text/plain',
            "pdf": 'application/pdf',
            "php": 'application/x-httpd-php',
            "jpg": 'image/jpeg',
            "png": 'image/png',
            "gif": 'image/gif',
            "bmp": 'image/bmp',
            "txt": 'text/plain',
            "doc": 'application/msword',
            "js": 'text/js',
            "swf": 'application/x-shockwave-flash',
            "mp3": 'audio/mpeg',
            "zip": 'application/zip',
            "rar": 'application/rar',
            "tar": 'application/tar',
            "arj": 'application/arj',
            "cab": 'application/cab',
            "html": 'text/html',
            "htm": 'text/html',
            "default": 'application/octet-stream',
            "audio": 'application/vnd.google-apps.audio',
            "Google Docs": 'application/vnd.google-apps.document',
            "Google Drawing": 'application/vnd.google-apps.drawing',
            "Google Drive file": 'application/vnd.google-apps.file',
            "Google Forms": 'application/vnd.google-apps.form',
            "Google Fusion Tables": 'application/vnd.google-apps.fusiontable',
            "Google My Maps": 'application/vnd.google-apps.map',
            "Google Photos": 'application/vnd.google-apps.photo',
            "Google Slides": 'application/vnd.google-apps.presentation',
            "Google Apps Scripts": 'application/vnd.google-apps.script',
            "Google Sites": 'application/vnd.google-apps.site',
            "Google Sheets": 'application/vnd.google-apps.spreadsheet',
            "3rd party shortcut": 'application/vnd.google-apps.drive-sdk',
            "folder": 'application/vnd.google-apps.folder'
        }
        promptMessage = 'Choose a media type to filter \n(press SPACE to mark, ENTER to continue, s to stop):'
        title = promptMessage
        options = [x for x in mimeTypes.keys()]
        picker = Picker(options, title, multi_select=True,
                        min_selection_count=1)
        picker.register_custom_handler(ord('s'), go_back)
        selected = picker.start()
        if type(selected) == list:
            query += "and ("
            for types in selected:
                query += "mimeType='" + mimeTypes[types[0]] + "' or "
            query = query[:-3]
            query += ")"
        if (not name) and types:
            query = query[4:]
    if pid:
        parent = click.prompt('enter the fid of parent or  sharing link')
        fid = utils.get_fid(parent)
        if (name != False) or (types != False):
            query += " and "
        query += "'" + fid + "' in parents"
    i = 1
    while True:
        response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name,mimeType,modifiedTime)',
                                        pageToken=page_token).execute()

        templist = [response.get('files', [])[i:i + 25] for i in range(0, len(
            response.get('files', [])), 25)]
        for item in templist:
            t = PrettyTable(['Sr.', 'Name', 'ID', 'Type', 'Modified Time'])
            for fils in item:
                t.add_row([i, fils.get('name')[:25], fils.get('id'), fils.get(
                    'mimeType').replace('application/', '')[:25], fils.get('modifiedTime')])
                i += 1
            print(t)
            click.confirm('Do you want to continue?', abort=True)
            click.clear()
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break