from __future__ import print_function
import os
import sys
import io
import re
import getpass
import subprocess
import requests
import click
import json
import time
import colorama
from pick import pick
from pick import Picker
from prettytable import PrettyTable
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
from httplib2 import Http
from oauth2client import file, client, tools
from .utils import MIMETYPES
import pyfiglet

dirpath = os.path.dirname(os.path.realpath(__file__))
SCOPES = 'https://www.googleapis.com/auth/drive'

def login():
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    if not creds or creds.invalid:
        client_id = os.path.join(dirpath,'oauth.json')
        flow = client.flow_from_clientsecrets(client_id,SCOPES)
        flags=tools.argparser.parse_args(args=[])
        creds = tools.run_flow(flow, store,flags)
        click.secho("********************** welcome to **********************",bold=True,fg='red') 
        result = pyfiglet.figlet_format("Drive - CLI", font = "slant" ) 
        click.secho(result,fg='yellow')
        click.secho("********************************************************",bold=True,fg='red')

def go_back(picker):
	return None, -1

def drive_data(*argv):
	dclipath = os.path.join(dirpath,'.drivecli')
	if not os.path.isfile(dclipath):
			with open(dclipath,'w')as outfile:
				if(not len(argv)):
					data = {}
				else:
					data = argv[0]
				json.dump(data,outfile)
	else:
		if(not len(argv)):
			with open(dclipath, 'r') as infile:
				data = json.load(infile)
		else:
			with open(dclipath,'w') as outfile:
				data = argv[0]
				json.dump(data,outfile)
	return data

def get_request(service,fid,mimeType):
    if(re.match('^application/vnd\.google-apps\..+',mimeType)):
        if(mimeType == 'application/vnd.google-apps.document'):
            mimeTypes={
                "pdf": 'application/pdf',
                "txt":'text/plain',
                "doc":'application/msword',
                "zip":'application/zip',
                "html":'text/html',
                "rtf":"application/rtf",
                "odt":"application/vnd.oasis.opendocument.text"
		    }
        elif(mimeType == 'application/vnd.google-apps.spreadsheet'):
            mimeTypes={
                "pdf": 'application/pdf',
                "xlsx" :'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                "zip":'application/zip',
                "html":'text/html',
                "ods":'application/vnd.oasis.opendocument.spreadsheet',
                "csv":'text/plain',
                "tsv":"text/tab-separated-values" ,
		    }
        elif(mimeType == 'application/vnd.google-apps.presentation'):
            mimeTypes={
                "pdf": 'application/pdf',
                "zip":'application/zip',
                "html":'text/html',
                "pptx":"application/vnd.openxmlformats-officedocument.presentationml.presentation",
                "plain txt":'text/plain'
		    }
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
                "htm":'text/html'
            }
        promptMessage = 'Choose type to export to \n(ENTER to select, s to stop):'
        title = promptMessage
        options = [x for x in mimeTypes.keys()]
        picker = Picker(options, title, indicator = '=>', default_index = 0)
        picker.register_custom_handler(ord('s'),  go_back)
        chosen, index = picker.start()
        if index!=-1:
            request = service.files().export_media(fileId=fid,mimeType=mimeTypes[chosen])
            return request,str("."+chosen)
        else:
            sys.exit(0)
    else:
        request = service.files().get_media(fileId=fid)
        return request,""

def write_needed(dir_name,item,sync_time):
    drive_time = time.mktime(time.strptime(item['modifiedTime'],'%Y-%m-%dT%H:%M:%S.%fZ'))
    local_time = os.path.getmtime(dir_name)
    #print(dir_name)
    #print(time.time(),"||",drive_time,"||",local_time,"||",sync_time)
    sync_time-=float(19800.00)
    local_time-=float(19800.00)
    c_time = time.time()-float(19800.00)
    if(sync_time<drive_time):
        if(sync_time<local_time):
            input=''
            while(input!='s' and input!='o'):
                input = click.prompt("Conflict: both local and online copy of "+dir_name+" has been modified\npress o to OVERWRITE s to SKIP")
            if(input=='o'):
                return True
        else:
            return True
    return False

def push_needed(drive,item_path):
    drive_time = time.mktime(time.strptime(drive['modifiedTime'],'%Y-%m-%dT%H:%M:%S.%fZ'))
    local_time = os.path.getmtime(item_path)-float(19801.00)
    #print(drive_time<local_time)
    return drive_time>local_time

def modified_or_created(sync_time,item_path):
    mtime = os.path.getmtime(item_path)
    ctime = os.path.getctime(item_path)
    #print(ctime,mtime,sync_time,int(time.time()))
    if(ctime>(sync_time+1.000)):
        click.echo("changed: "+item_path)
        return 1
    elif(mtime>(sync_time+1.000)):
        click.echo("changed: "+item_path)
        return 1
    return 0

def get_fid(inp):
    if 'drive' in inp:
        if 'open' in link:
            fid = link.split('=')[-1]
        else:
            fid = link.split('/')[-1].split('?')[0]
    else:
        fid = inp
    return inp

def create_new(cwd,fid,exist=False):
    if not exist:
        os.mkdir(cwd)
    data = drive_data()
    data[cwd] = {}
    data[cwd]['id'] = fid
    data[cwd]['time'] = time.time()
    drive_data(data)

def delete_file(fid):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v2', http=creds.authorize(Http()))
    fid = fid['id']
    try:
        service.files().delete(fileId=fid).execute()
    except:
        click.secho("Error Ocurred:\n make sure that you have appropriate access",fg='red')

def get_file(fid):
    data=drive_data()
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    files = service.files().get(fileId=fid).execute()
    return files

def get_child(cwd):
    # print(fid)
    data=drive_data()
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    drive_lis = {}
    query = "'"+data[cwd]['id']+"' in parents"
    # print(query) 
    while True:
        children = service.files().list(q=query,
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

def get_child_id(pid,item):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    query = "name = '"+item+"' and "
    query = "'"+pid+"' in parents"
    response = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id, name)',
                                        pageToken=page_token).execute()
    fils = response.get('files', [])[0]
    return fils.get('id')

def create_dir(cwd,pid,name):
    file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents':[pid]
        }
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    fid = service.files().create(body=file_metadata,fields='id').execute()
    fid['time']=time.time()
    full_path = os.path.join(cwd,name)
    #print(full_path)
    data = drive_data()
    data[full_path] = fid
    drive_data(data)
    click.secho("Created a tracked directory",fg='magenta')
    return full_path,fid['id']

def file_download(item,cwd,sync_time=time.time()):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    fid = item['id']
    fname = item['name']
    fh = io.BytesIO()
    files = service.files().get(fileId=fid).execute()
    click.echo("Preparing: "+click.style(fname,fg='red')+" for download")
    request,ext= get_request(service,fid,item['mimeType'])
    file_path=(os.path.join(cwd,fname)+ext)
    if((os.path.exists(file_path)) and (not write_needed(file_path,item,sync_time))):
        return
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    with click.progressbar(length=100,label='downloading file') as bar:
        pstatus=0
        while done is False:
            status, done = downloader.next_chunk()
            status=int(status.progress() * 100)
            bar.update(int(status-pstatus))
            pstatus=status
        with open(file_path, 'wb') as f: #add dynamic name
            f.write(fh.getvalue())
    click.secho("completed download of "+fname,fg='yellow')

def identify_mimetype(name):
    extension = "."+str(name.split('.')[-1])
    if(extension in MIMETYPES.keys()):
        return MIMETYPES[extension]
    else:
        return 'application/octet-stream'

def upload_file(name,path,pid):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    file_mimeType = identify_mimetype(name)
    file_metadata = {   
                        'name':name,
                        'parents':[pid],
                        'mimeType':file_mimeType
                    }
    media = MediaFileUpload(path,mimetype=file_mimeType)
    new_file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
    click.secho("uploaded "+name,fg='yellow')
    return new_file

def update_file(name,path,fid):
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    file_mimeType = identify_mimetype(name)
    media = MediaFileUpload(path,mimetype=file_mimeType)
    new_file = service.files().update(fileId=fid,
                                        media_body=media,
                                        fields='id').execute()
    return new_file

def pull_content(cwd,fid):
    data=drive_data()
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    lis = []
    query = "'"+data[cwd]['id']+"' in parents" 
    while True:
        children = service.files().list(q=query,
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
        dir_name = os.path.join(cwd,item['name'])
        if(item['mimeType']!='application/vnd.google-apps.folder'):
            if((not os.path.exists(dir_name)) or write_needed(dir_name,item,data[cwd]['time'])):
                file_download(item,cwd,data[cwd]['time'])
        else:
            if(not os.path.exists(dir_name)):
                click.secho("creating: "+dir_name)
                os.mkdir(dir_name)
                data=drive_data()
                data[dir_name]={'id':item['id'],'time':time.time()}
                data=drive_data(data)
            else:
                click.secho("updating: "+dir_name)
            pull_content(dir_name,item['id'])
    data=drive_data()      
    data[cwd]['time']=time.time()
    data=drive_data(data)
    drive_data(data)

def list_status(cwd,sync_time):
    local_lis = os.listdir(cwd)
    changes = 0
    for item in local_lis:
        item_path = os.path.join(cwd,item)
        if(os.path.isdir(item_path)):
            if(modified_or_created(sync_time,item_path)):
                changes += 1
                data = drive_data()
                if item in data.keys(): 
                    sync_time = data[item]
                else:
                    sync_time = float(0)
                list_status(item_path,sync_time)  
        else:
            changes += modified_or_created(sync_time,item_path)
    if changes == 0:
        click.secho("No changes made since the last sync")

def push_content(cwd,fid):
    drive_lis = get_child(cwd)
    local_lis = os.listdir(cwd)
    data = drive_data()
    sync_time = data[cwd]['time']
    #print(local_lis,"\n",drive_lis.keys())
    for item in local_lis:
        item_path = os.path.join(cwd,item)
        if(os.path.isdir(item_path)):
            if item not in drive_lis.keys():
                child_cwd,child_id = create_dir(cwd,fid,item)
            else:
                child_cwd = os.path.join(cwd,item)
                child_id = drive_lis[item]['id']
                if child_cwd not in data.keys():
                    data[child_cwd] = {'id':child_id,'time':time.time()}
                    data = drive_data(data)
            push_content(child_cwd,child_id)
        else:
            item_path = os.path.join(cwd,item)
            if item not in drive_lis.keys():
                click.secho("uploading "+item)
                upload_file(item,item_path,fid)
            else:
                if(push_needed(drive_lis[item],item_path)):
                    click.secho("updating "+item)
                    cid = get_child_id(fid,item)
                    update_file(item,item_path,cid)
                    click.secho("updating of "+item+" completed",fg='yellow')
    data = drive_data()
    data[cwd]['time']=time.time()
    drive_data(data)



@click.group()
def cli():
    login()

@cli.command('login',short_help='login to your google account and authenticate the service')
def loggin():
    pass

@cli.command('view-files',short_help='filter search files and file ID for files user has access to')
@click.option('--name',is_flag=bool,help='provide username in whose repos are to be listed.')
@click.option('--types',is_flag=bool,help='provide username in whose repos are to be listed.')
def viewFile(name,types):
    """
    view-files: Filter based list of the names and ids of the first 10 files the user has access to
    """
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    query=""
    if name:
        q_name=click.prompt('enter the search value')
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
    i = 1
    while True:
        response = service.files().list(q=query,
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name,mimeType,modifiedTime)',
                                            pageToken=page_token).execute() 
        
        templist = [response.get('files', [])[i:i+25] for i in range(0, len(response.get('files', [])), 25)] #breakdown list to 25 entries at a time
        for item in templist:
            t = PrettyTable(['Sr.','Name','ID','Type','Modified Time'])                                  
            for fils in item: 
                t.add_row([i,fils.get('name')[:25], fils.get('id'),fils.get('mimeType').replace('application/','')[:25],fils.get('modifiedTime')])
                i+=1
            print(t)
            click.confirm('Do you want to continue?',abort=True)
            click.clear()
        page_token = response.get('nextPageToken', None)
        if page_token is None:
            break

@cli.command('clone',short_help='download any file using sharing link or file ID it will be automatically tracked henceforth')
@click.option('--link',help='give sharing link of the file')
@click.option('--id',help='give file id of the file')
def download(link,id):
    '''
    clone: download a file/folder  using either the sharing link or using the file ID  for the file
    '''
    if id != None :
        fid = id
    elif link != None :
        if 'open' in link:
            fid = link.split('=')[-1]
        else:
            fid = link.split('/')[-1].split('?')[0]
    else:
        click.secho("argument error",fg='red')
        with click.Context(download) as ctx:
                click.echo(download.get_help(ctx))
        sys.exit(0)
    clone = get_file(fid)
    cwd = os.getcwd()
    if clone['mimeType'] == 'application/vnd.google-apps.folder':
        new_dir = os.path.join(cwd,clone['name'])
        create_new(new_dir,fid)
        pull_content(new_dir,fid)
    else:
        file_download(clone,cwd)

@cli.command('add_remote',short_help='upload any existing file to drive')
@click.option('--file',help='specify the partcular file to uploaded else entire directory is uploaded')
@click.option('--pid',help='specify particular folder id/sharing_link of the folder under which remote must must be added')
def create_remote(file,pid):
    """
    add_remote: create remote equivalent for existing file/folder in local device
    """
    cwd = os.getcwd()
    if pid == None :
        pid = 'root'
    if file != None :
        file_path = os.path.join(cwd,file)
        if os.path.isfile(file_path):
            upload_file(file,file_path,pid)
        else:
            click.secho("No such file exist: "+file_path,fg="red")
            with click.Context(create_remote) as ctx:
                click.echo(create_remote.get_help(ctx))
    else:
        sep = os.sep
        dir_cd,name = sep.join(cwd.split(sep)[:-1]),cwd.split(sep)[-1]
        child_cwd,child_id = create_dir(dir_cd,pid,name)
        push_content(child_cwd,child_id)
    if pid != None :
        parent_file = get_file(pid)
        parent_name = parent_file['name'] 
        click.secho("content added under directory "+parent_name,fg='magenta')

@cli.command('rm',short_help='delete a particular file in drive')
@click.option('--file',help='specify the partcular file to deleted else entire directory is deleted')
@click.option('--id',help='delete untracked file directly using id or sharing link, can be used even for unlinked files')
def delete(file,id):
    '''
    rm: delete a particular file/folder from the directory in the remote drive
    '''
    cwd = os.getcwd()
    if id == None:
        if file != None:
            file_path = os.path.join(cwd,file)
            if os.path.isfile(file_path):
                local_dir = get_child(cwd)
                fid = local_dir[file]
            else:
                click.secho("No such file exist: "+file_path,fg="red")
                with click.Context(delete) as ctx:
                    click.echo(delete.get_help(ctx))
            cwd = file_path
        else:
            data = drive_data()
            fid = data[cwd]
            data.pop(cwd,None)
            drive_data(data)
        delete_file(fid)
    else:
        fid = get_fid(id)
        delete_file(fid)

@cli.command('ls',short_help='list out all the files present in this directory in the drive for tracked directories')
def list_out():
    """
    ls: Print files belonging to a folder in the drive folder of the current directory
    """
    data = drive_data()
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    lis = []
    cwd = os.getcwd()
    if cwd not in data.keys():
        click.secho("following directory has not been tracked: \nuse drive add_remote or drive clone",fg='red')
        sys.exit(0)
    query = "'"+data[cwd]['id']+"' in parents"
    #print(query)
    t = PrettyTable(['Name','File ID','Type'])  
    while True:
        children = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id,mimeType,name)',
                                        pageToken=page_token
                                        ).execute()                                 
        for child in children.get('files', []):
            t.add_row([child.get('name')[:25], child.get('id'),child.get('mimeType')])
        page_token = children.get('nextPageToken', None)
        if page_token is None:
            break
    print(t)

@cli.command('status',short_help='list changes commited since last sync')
def status():
    '''
    status: get a change log of files changed since you had the last sync(push/pull/clone)
    '''
    cwd = os.getcwd()
    data = drive_data()
    if cwd not in data.keys():
        click.secho("following directory has not been tracked: \nuse drive add_remote or drive clone ",fg='red')
        sys.exit(0)
    sync_time = data[cwd]['time']
    list_status(cwd,sync_time)

@cli.command('pull',short_help='get latest updates from online drive of the file')
def pull():
    data=drive_data()
    cwd=os.getcwd()
    if cwd not in data.keys():
        click.secho("following directory has not been tracked: \nuse drive add_remote or drive clone ",fg='red')
        sys.exit(0)
    fid=data[cwd]['id']
    syn_time=data[cwd]['time']
    pull_content(cwd,fid)

@cli.command('push',short_help='push modification from local files to the drive')
def push():
    '''
    push the latest changes from your local folder that has been added/cloned to google drive.
    '''
    data=drive_data()
    cwd=os.getcwd()
    if cwd not in data.keys():
        click.secho("following directory has not been tracked: \nuse drive add_remote or drive clone ",fg='red')
        sys.exit(0)
    fid=data[cwd]['id']
    syn_time=data[cwd]['time']
    push_content(cwd,fid)

@cli.command('logout',short_help='logout from the account logged in with')
def destroyToken():
    '''
    logout: logout from the account that has been logged in
    '''
    token = os.path.join(dirpath,'token.json')
    store = file.Storage(token)
    creds = store.get()
    if creds:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
        params={'token': creds.access_token},
        headers = {'content-type': 'application/x-www-form-urlencoded'})
    
    os.remove(token)
    click.secho("Logged Out successfully\nUse:") 
    click.secho("drive login",bold=True,fg='green') 
    click.secho("to login again")

if __name__ == '__main__':
    login()