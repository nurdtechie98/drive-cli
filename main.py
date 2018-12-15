from __future__ import print_function
import os
import sys
import io
import getpass
import subprocess
import requests
import click
import json
import warnings
import colorama
from pick import pick
from pick import Picker
from prettytable import PrettyTable
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from httplib2 import Http
from oauth2client import file, client, tools

dirpath = os.path.dirname(os.path.realpath(__file__))
SCOPES = 'https://www.googleapis.com/auth/drive'

def login():
    with warnings.catch_warnings():
        token = os.path.join(dirpath,'token.json')
        store = file.Storage(token)
        creds = store.get()
        if not creds or creds.invalid:
            client_id = os.path.join(dirpath,'client_id.json')
            flow = client.flow_from_clientsecrets(client_id,SCOPES)
            creds = tools.run_flow(flow, store)  

def go_back(picker):
	return None, -1

@click.group()
def cli():
    login()

# @cli.command('login',short_help='create a new repo in Github and add remote origin to the local project.')
# def loggin():
#     with warnings.catch_warnings():
#         token = os.path.join(dirpath,'token.json')
#         store = file.Storage(token)
#         creds = store.get()
#         if not creds or creds.invalid:
#             client_id = os.path.join(dirpath,'client_id.json')
#             flow = client.flow_from_clientsecrets(client_id,SCOPES)
#             creds = tools.run_flow(flow, store)

@cli.command('view-files',short_help='create a new repo in Github and add remote origin to the local project.')
@click.option('--name',is_flag=bool,help='provide username in whose repos are to be listed.')
@click.option('--types',is_flag=bool,help='provide username in whose repos are to be listed.')
def viewFile(name,types):
    """
    Prints the names and ids of the first 10 files the user has access to.
    """
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    query=""
    if name:
        q_name=click.prompt('enter search search value')
        query="name contains '"+q_name+"' "
    if types:
        mimeTypes={
			"xls":'application/vnd.ms-excel',
    		"xlsx" :'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    		"xml" :'text/xml',
    		"ods":'application/vnd.oasis.opendocument.spreadsheet',
    		"csv":'text/plain',
    		"tmpl":'text/plain',
    		"pdf": 'application/pdf',
    		"php":'application/x-httpd-php',
    		"jpg":'image/jpeg',
    		"png":'image/png',
    		"gif":'image/gif',
    		"bmp":'image/bmp',
    		"txt":'text/plain',
    		"doc":'application/msword',
    		"js":'text/js',
    		"swf":'application/x-shockwave-flash',
    		"mp3":'audio/mpeg',
    		"zip":'application/zip',
    		"rar":'application/rar',
    		"tar":'application/tar',
    		"arj":'application/arj',
    		"cab":'application/cab',
    		"html":'text/html',
    		"htm":'text/html',
    		"default":'application/octet-stream',
            "audio":'application/vnd.google-apps.audio',	
            "Google Docs":'application/vnd.google-apps.document',
            "Google Drawing":'application/vnd.google-apps.drawing',
            "Google Drive file":'application/vnd.google-apps.file',	
            "Google Forms":'application/vnd.google-apps.form',	
            "Google Fusion Tables":'application/vnd.google-apps.fusiontable',	
            "Google My Maps":'application/vnd.google-apps.map',	
            "Google Photos":'application/vnd.google-apps.photo',	
            "Google Slides":'application/vnd.google-apps.presentation',	
            "Google Apps Scripts":'application/vnd.google-apps.script',	
            "Google Sites":'application/vnd.google-apps.site',	
            "Google Sheets":'application/vnd.google-apps.spreadsheet',	
            "3rd party shortcut":'application/vnd.google-apps.drive-sdk',	
    		"folder":'application/vnd.google-apps.folder'
		}
        promptMessage = 'Choose a media type to filter \n(press SPACE to mark, ENTER to continue, s to stop):'
        title = promptMessage
        options = [x for x in mimeTypes.keys()]
        picker = Picker(options, title, multi_select=True, min_selection_count=1)
        picker.register_custom_handler(ord('s'),go_back)
        selected = picker.start()
        if type(selected) == list:
            query+="and ("
            for types in selected:
                query+="mimeType='"+mimeTypes[types[0]]+"' or "
            query=query[:-3]
            query+=")"
        if (not name) and types:
            query=query[4:]
    while True:
        response = service.files().list(q=query,
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute() 
        t = PrettyTable(['Name','ID'])                                  
        for fils in response.get('files', []):
            t.add_row([fils.get('name')[:25], fils.get('id')])
        print(t)
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
        click.confirm('Do you want to continue?',abort=True)
        click.clear()

@cli.command('logout',short_help='logout from the account')
def destroyToken():
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    if creds:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': creds.access_token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
    
    os.remove(token)

@cli.command('download',short_help='download any file whose file ID is known')
@click.option('--fid',prompt=True,help='give file id of the file')
@click.option('--expas',is_flag=bool,help='export flag as a particular type')
def download(fid,expas):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    if not expas:
        request = service.files().get_media(fileId=fid)
    else:
        mimeTypes={
    		"ods":'application/vnd.oasis.opendocument.spreadsheet',
    		"csv":'text/plain',
    		"tmpl":'text/plain',
    		"pdf": 'application/pdf',
    		"php":'application/x-httpd-php',
    		"jpg":'image/jpeg',
    		"png":'image/png',
    		"gif":'image/gif',
    		"bmp":'image/bmp',
    		"txt":'text/plain',
    		"doc":'application/msword',
    		"js":'text/js',
    		"swf":'application/x-shockwave-flash',
    		"mp3":'audio/mpeg',
    		"zip":'application/zip',
    		"rar":'application/rar',
    		"tar":'application/tar',
    		"arj":'application/arj',
    		"cab":'application/cab',
    		"html":'text/html',
    		"htm":'text/html',
    		"default":'application/octet-stream',
    		"folder":'application/vnd.google-apps.folder'
		}
        promptMessage = 'Choose type to export to \n(press SPACE to mark, ENTER to continue, s to stop):'
        title = promptMessage
        options = [x for x in mimeTypes.keys()]
        picker = Picker(options, title, indicator = '=>', default_index = 0)
        picker.register_custom_handler(ord('s'),  go_back)
        chosen, index = picker.start()
        if index!=-1:
            request = service.files().export_media(fileId=fid,mimeType=mimeTypes[chosen])
        else:
            sys.exit(0)
    fh = io.BytesIO()
    files = service.files().get(fileId=fid).execute()
    click.echo("Preparing: "+click.style(files['name'],fg='red')+" for download")
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    with click.progressbar(length=100,label='downloading file') as bar:
        pstatus=0
        while done is False:
            status, done = downloader.next_chunk()
            status=int(status.progress() * 100)
            bar.update(int(status-pstatus))
            pstatus=status
        with open('file.docs', 'wb') as f: #add dynamic name
            f.write(fh.getvalue())
if __name__ == '__main__':
    login()