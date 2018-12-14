from __future__ import print_function
import os
import sys
import getpass
import subprocess
import requests
import click
import json
import colorama
from pick import pick
from pick import Picker
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive'

def login():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_id.json', SCOPES)
        creds = tools.run_flow(flow, store)

@click.group()
def cli():
    login()

@cli.command('view-files',short_help='create a new repo in Github and add remote origin to the local project.')
@click.option('--name',prompt=True,help='provide username in whose repos are to be listed.')
@click.option('--type',prompt=True,help='provide username in whose repos are to be listed.')
def main(name,type):
    """
    Prints the names and ids of the first 10 files the user has access to.
    """
    store = file.Storage('token.json')
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    query=""
    if name!=" ":
        query="name contains '"+name+"' "
    if type!=" ":
        query+="and mimeType='"+type+"'"
    if name==" ":
        query=query[4:]
    while True:
        response = service.files().list(q=query,
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute()                                   
        for fils in response.get('files', []):
            print('Found file: %s (%s)' % (fils.get('name'), fils.get('id')))
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break
        click.confirm('Do you want to continue?',abort=True)
        click.clear()

@cli.command('logout',short_help='logout from the account')
def destroy_token():
    store = file.Storage('token.json')
    creds = store.get()
    if creds:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': creds.access_token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
    os.remove('token.json')

if __name__ == '__main__':
    login()