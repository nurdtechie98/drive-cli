from . import utils
import os
import sys
import click
from pick import Picker
from httplib2 import Http
from oauth2client import file
from prettytable import PrettyTable
from googleapiclient.discovery import build
from prettytable import MSWORD_FRIENDLY
from mimetypes import MimeTypes


dirpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirpath)
mime = MimeTypes()


@click.command('view-files', short_help='filter search files and file ID for files user has access to')
@click.option('--name', is_flag=bool, help='provide username in whose repos are to be listed.')
@click.option('--types', is_flag=bool, help='provide username in whose repos are to be listed.')
@click.option('--pid', is_flag=bool, help='provide parent file ID or sharing link and list its child file/folders.')
def view_file(name, types, pid):
    """
    view-files: Filter based list of the names and ids of the first 10 files the user has access to
    """
    cwd = os.getcwd()
    flags = {"--name": [None], "--types": [None], "--pid": [None]}
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    query = ""
    if name:
        q_name = click.prompt('enter the search value')
        flags["--name"] = [q_name]
        query = "name contains '" + q_name + "' "
    if types:
        mimeTypes = {extension: mime.guess_type("placeholder_filename." + extension)[0] for extension
                     in ("xls",
                         "xlsx",
                         "xml",
                         "ods",
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
        mimeTypes.update({'tmpl': 'text/plain',
                          'php': 'application/x-httpd-php',
                          'arj': 'application/arj',
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
                          "folder": 'application/vnd.google-apps.folder'})
        promptMessage = 'Choose a media type to filter \n(press SPACE to mark, ENTER to continue, s to stop):'
        title = promptMessage
        options = [x for x in mimeTypes.keys()]
        picker = Picker(options, title, multi_select=True,
                        min_selection_count=1)
        picker.register_custom_handler(ord('s'), utils.go_back)
        selected = picker.start()
        option = []
        if isinstance(selected, list):
            query += "and ("
            for types in selected:
                query += "mimeType='" + mimeTypes[types[0]] + "' or "
                option.append(types[0])
            query = query[:-3]
            query += ")"
            flags["--types"] = option
        if (not name) and types:
            query = query[4:]
    if pid:
        parent = click.prompt('enter the fid of parent or  sharing link')
        flags["--pid"] = [parent]
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

        templist = [response.get('files', [])[j:j + 25] for j in range(0, len(
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
    utils.save_history([flags, "", cwd])


@click.command('clone', short_help='download any file using sharing link or file ID it will be automatically tracked henceforth')
@click.argument('payload')
def download(payload):
    '''
    clone: download a file/folder  using either the sharing link or using the file ID  for the file
    '''
    cwd = os.getcwd()
    utils.save_history([{}, payload, cwd])
    if payload != None:
        fid = utils.get_fid(payload)
    else:
        click.secho("argument error", fg='red')
        with click.Context(download) as ctx:
            click.echo(download.get_help(ctx))
        sys.exit(0)
    clone = utils.get_file(fid)
    click.secho("cloning into '" + clone['name'] + "' .....", fg='magenta')
    if clone['mimeType'] == 'application/vnd.google-apps.folder':
        new_dir = os.path.join(cwd, clone['name'])
        utils.create_new(new_dir, fid)
        utils.pull_content(new_dir, fid)
    else:
        utils.file_download(clone, cwd)
    click.secho("cloning of " + clone['name'] + ' completed', fg='green')


@click.command('add_remote', short_help='upload any existing file to drive')
@click.option('--file', help='specify the partcular file to uploaded else entire directory is uploaded')
@click.option('--pid', help='specify particular folder id/sharing_link of the folder under which remote must must be added')
def create_remote(file, pid):
    """
    add_remote: create remote equivalent for existing file/folder in local device
    """
    cwd = os.getcwd()
    utils.save_history([{"--file": [file], "--pid":[pid]}, "", cwd])
    if pid == None:
        pid = 'root'
    if file != None:
        file_path = os.path.join(cwd, file)
        if os.path.isfile(file_path):
            utils.upload_file(file, file_path, pid)
        else:
            click.secho("No such file exist: " + file_path, fg="red")
            with click.Context(create_remote) as ctx:
                click.echo(create_remote.get_help(ctx))
    else:
        sep = os.sep
        dir_cd, name = sep.join(cwd.split(sep)[:-1]), cwd.split(sep)[-1]
        child_cwd, child_id = utils.create_dir(dir_cd, pid, name)
        utils.push_content(child_cwd, child_id)
    if pid != None:
        parent_file = utils.get_file(pid)
        parent_name = parent_file['name']
        click.secho("content added under directory " +
                    parent_name, fg='magenta')


@click.command('rm', short_help='delete a particular file in drive')
@click.option('--file', help='specify the partcular file to deleted else entire directory is deleted')
@click.option('--id', help='delete untracked file directly using id or sharing link, can be used even for unlinked files')
def delete(file, id):
    '''
    rm: delete a particular file/folder from the directory in the remote drive
    '''
    cwd = os.getcwd()
    utils.save_history([{"--file": [file], "--id":[id]}, "", cwd])
    if id == None:
        if file != None:
            file_path = os.path.join(cwd, file)
            if os.path.isfile(file_path):
                local_dir = utils.get_child(cwd)
                fid = local_dir[file]
            else:
                click.secho("No such file exist: " + file_path, fg="red")
                with click.Context(delete) as ctx:
                    click.echo(delete.get_help(ctx))
            cwd = file_path
        else:
            data = utils.drive_data()
            fid = data[cwd]
            data.pop(cwd, None)
            utils.drive_data(data)
        utils.delete_file(fid)
    else:
        fid = utils.get_fid(id)
        utils.delete_file(fid)


@click.command('ls', short_help='list out all the files present in this directory in the drive for tracked directories')
def list_out():
    """
    ls: Print files belonging to a folder in the drive folder of the current directory
    """
    cwd = os.getcwd()
    utils.save_history([{}, "", cwd])
    data = utils.drive_data()
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    if cwd not in data.keys():
        click.secho(
            "following directory has not been tracked: \nuse drive add_remote or drive clone", fg='red')
        sys.exit(0)
    query = "'" + data[cwd]['id'] + "' in parents"
    click.secho('listing down files in drive ....', fg='magenta')
    t = PrettyTable(['Name', 'File ID', 'Type'])
    while True:
        children = service.files().list(q=query,
                                        spaces='drive',
                                        fields='nextPageToken, files(id,mimeType,name)',
                                        pageToken=page_token
                                        ).execute()
        for child in children.get('files', []):
            t.add_row([child.get('name')[:25], child.get(
                'id'), child.get('mimeType')])
        page_token = children.get('nextPageToken', None)
        if page_token is None:
            break
    print(t)


@click.command('cat', short_help='view contents of the file using its file id or sharing link')
@click.argument('link')
def view(link):
    cwd = os.getcwd()
    utils.save_history([{}, link, cwd])
    fid = utils.get_fid(link)
    utils.concat(fid)


@click.command('status', short_help='list changes committed since last sync')
def status():
    '''
    status: get a change log of files changed since you had the last sync(push/pull/clone)
    '''
    cwd = os.getcwd()
    utils.save_history([{}, "", cwd])
    data = utils.drive_data()
    if cwd not in data.keys():
        click.secho(
            "following directory has not been tracked: \nuse drive add_remote or drive clone ", fg='red')
        sys.exit(0)
    sync_time = data[cwd]['time']
    utils.list_status(cwd, sync_time)


@click.command('pull', short_help='get latest updates from online drive of the file')
def pull():
    cwd = os.getcwd()
    utils.save_history([{}, "", cwd])
    data = utils.drive_data()
    if cwd not in data.keys():
        click.secho(
            "following directory has not been tracked: \nuse drive add_remote or drive clone ", fg='red')
        sys.exit(0)
    fid = data[cwd]['id']
    current_root = utils.get_file(fid)
    click.secho("checking for changes in '" +
                current_root['name'] + "' ....", fg='magenta')
    utils.pull_content(cwd, fid)
    click.secho(current_root['name'] +
                " is up to date with drive", fg='yellow')


@click.command('push', short_help='push modification from local files to the drive')
def push():
    '''
    push the latest changes from your local folder that has been added/cloned to google drive.
    '''
    cwd = os.getcwd()
    utils.save_history([{}, "", cwd])
    data = utils.drive_data()
    if cwd not in data.keys():
        click.secho(
            "following directory has not been tracked: \nuse drive add_remote or drive clone ", fg='red')
        sys.exit(0)
    fid = data[cwd]['id']
    current_root = utils.get_file(fid)
    click.secho("checking for changes in '" +
                current_root['name'] + "' ....", fg='magenta')
    utils.push_content(cwd, fid)
    click.secho("Working directory is clean", fg="green")


role_help = """provide role to grant permission accordingly, following roles are currently allowed :
                * owner
                * writer
                * reader
                [Default]:reader
"""
type_help = """type of grantee, following are currently available :
                * user
                * group
                * anyone
                [Default]:user
"""
message_help = """provide a short message you want to send
                [Default]:'shared via drive-cli'
"""


@click.command('share', short_help="share file using file id or link")
@click.argument('fid')
@click.option('--role', default="reader", help=role_help)
@click.option('--type', default="user", help=type_help)
@click.option('--message', default="shared via drive-cli", help=message_help)
def share(fid, role, type, message):
    '''
    share file/folder using using either the sharing link or using the file ID
    '''
    cwd = os.getcwd()
    flags = {"--role": [role], "--type": [type], "--message": [message]}
    click.secho("updating share setting.....", fg='magenta')
    file_id = utils.get_fid(fid)
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    if(type == "anyone"):
        if(role == "owner"):
            transfer_ownership = True
        else:
            transfer_ownership = False
        request = {
            "role": role,
            "type": type,
            "allowFileDiscovery": True
        }
        try:
            response = service.permissions().create(body=request,
                                                    fileId=file_id,
                                                    transferOwnership=transfer_ownership,
                                                    fields='id').execute()
            if(list(response.keys())[0] == "error"):
                click.secho(response["error"]["message"], fg='red')
            else:
                share_link = "https://drive.google.com/open?id=" + file_id
                click.secho("share link : " + share_link)
        except:
            error_message = str(sys.exc_info()[1])
            error_message = error_message.split('\"')[1]
            click.secho(error_message, fg='red')

    else:
        if(type == "user"):
            email_id = click.prompt("Enetr email address of user ")
        else:
            email_id = click.prompt("Enetr email address of a google group ")
        flags["Email ID"] = email_id
        if(role == "owner"):
            transfer_ownership = True
        else:
            transfer_ownership = False
        request = {
            "role": role,
            "type": type,
            "emailAddress": email_id
        }
        try:
            response = service.permissions().create(body=request,
                                                    fileId=file_id,
                                                    emailMessage=message,
                                                    sendNotificationEmail=True,
                                                    transferOwnership=transfer_ownership,
                                                    fields='id').execute()
            if(list(response.keys())[0] == "error"):
                click.secho(response["error"]["message"], fg='red')
            else:
                click.secho("successfully share", fg='green')
        except:
            error_message = str(sys.exc_info()[1])
            error_message = error_message.split('\"')[1]
            click.secho(error_message, fg='red')
    utils.save_history([flags, fid, cwd])


@click.command('history', short_help="view history")
@click.option('--date', help="specify the date to filter out your history")
@click.option('--clear', is_flag=bool, help="clear entire histroy")
def history(date, clear):
    if clear:
        click.confirm('Do you want to continue?', abort=True)
        click.secho("deleting.....", fg='magenta')
        utils.clear_history()
        click.secho("successfully deleted", fg='green')
        cwd = os.getcwd()
        utils.save_history([{"--date": [date], "--clear":["True"]}, "", cwd])
    else:
        cwd = os.getcwd()
        utils.save_history([{"--date": [date], "--clear":[None]}, "", cwd])
        History = utils.get_history()
        if date != None:
            if date in History:
                history = History[date]
                for i in history:
                    click.secho(date + "  " + i, fg='yellow', bold=True)
                    click.secho("working directory : " + history[i]["cwd"], bold=True)
                    click.secho("command : " + history[i]["command"])
                    if(history[i]["arg"] != ""):
                        click.secho("argument : " + history[i]["arg"])
                    if(len(history[i]["flags"]) != 0):
                        flag_val = ""
                        for j in history[i]["flags"]:
                            if(history[i]["flags"][j][0] != None):
                                val = ", ".join(history[i]["flags"][j])
                                flag_val = flag_val + "\t" + j + " : " + val + "\n"
                        if(flag_val != ""):
                            click.secho("flags : ", bold=True)
                            click.secho(flag_val)
                    click.secho("\n")
            else:
                click.secho("No histrory found!!!", fg='red')
        else:
            if len(History) == 0:
                click.secho("No histrory found!!!", fg='red')
            else:
                for date in History:
                    history = History[date]
                    for i in history:
                        click.secho(date + "  " + i, fg='yellow', bold=True)
                        click.secho("working directory : " + history[i]["cwd"], bold=True)
                        click.secho("command : " + history[i]["command"])
                        if(history[i]["arg"] != ""):
                            click.secho("argument : " + history[i]["arg"])
                        if(len(history[i]["flags"]) != 0):
                            flag_val = ""
                            for j in history[i]["flags"]:
                                if(history[i]["flags"][j][0] != None):
                                    val = ", ".join(history[i]["flags"][j])
                                    flag_val = flag_val + "\t" + j + " : " + val + "\n"
                            if(flag_val != ""):
                                click.secho("flags : ", bold=True)
                                click.secho(flag_val)
                        click.secho("\n")


@click.command('log', short_help="It allows users to see who made edits and to revert to earlier versions of the same file.")
@click.argument('fid')
@click.option('--get', type=str, help="provide revision id to get more info ")
@click.option('--delete', type=str, help="delete a particular revision")
@click.option('--save', type=str, help="To keep revision forever, even if it is no longer the head revision. If not set, the revision will be automatically purged 30 days after newer content is uploaded. ")
def get_revision(fid, get, delete, save):
    '''
    It allows users to see who made edits and to revert to earlier versions of the same file.
    '''
    cwd = os.getcwd()
    flags = {"--get": [get], "--delete": [delete], "--save": [save]}
    utils.save_history([flags, fid, cwd])
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    if(get != None):
        click.secho("fetching....", fg='magenta')
        service = build('drive', 'v2', http=creds.authorize(Http()))
        file_id = utils.get_fid(fid)
        response = service.revisions().get(fileId=file_id,
                                           revisionId=get).execute()
        modified_time = response["modifiedDate"].split("T")
        user = response["lastModifyingUser"]
        click.secho(click.style("File : ", fg='yellow', bold=True) +
                    response["originalFilename"] + " " + response["mimeType"])
        click.secho(click.style("Link : ", fg='yellow',
                                bold=True) + response["selfLink"])
        click.secho(click.style("Author : ", fg='yellow', bold=True) +
                    response["lastModifyingUserName"] + " " + user["emailAddress"])
        click.secho(click.style("Date : ", fg='yellow', bold=True) +
                    modified_time[0] + " " + modified_time[1].split(".")[0])
        click.secho(click.style("File size : ", fg='yellow',
                                bold=True) + response["fileSize"] + "bytes")
        click.secho(click.style("eTag : ", fg='yellow',
                                bold=True) + response["etag"])
        if(response["published"]):
            click.secho(click.style("Published : ",
                                    fg='yellow', bold=True) + "Yes")
        else:
            click.secho(click.style("Published : ",
                                    fg='yellow', bold=True) + "No")
        if(response["pinned"]):
            click.secho(click.style(
                "Pinned : ", fg='yellow', bold=True) + "Yes")
        else:
            click.secho(click.style(
                "Pinned : ", fg='yellow', bold=True) + "No")
        click.secho(click.style("Permission Id : ", fg='yellow', bold=True) +
                    user["permissionId"])

    if(delete != None):
        click.secho("deleting.....", fg='magenta')
        service = build('drive', 'v3', http=creds.authorize(Http()))
        file_id = utils.get_fid(fid)
        response = service.revisions().delete(fileId=file_id,
                                              revisionId=delete).execute()
        click.secho("revision" + delete + "successfully deleted", fg='green')

    if(save != None):
        click.secho("saving " + save +
                    " revision premanently....", fg='magenta')
        service = build('drive', 'v3', http=creds.authorize(Http()))
        file_id = utils.get_fid(fid)
        response = service.revisions().update(body={"keepForever": True},
                                              fileId=file_id,
                                              revisionId=save).execute()
        click.secho("svaed successfully", fg='green')

    if(delete == None and get == None and save == None):
        file_id = utils.get_fid(fid)
        file_name = utils.get_file(fid)["name"]
        click.secho("fetching revision detail of " + file_name + ".....", fg='magenta')
        service = build('drive', 'v3', http=creds.authorize(Http()))
        response = service.revisions().list(fileId=file_id).execute()
        revisions = response["revisions"]
        for r in reversed(revisions):
            modified_time = r["modifiedTime"].split("T")
            click.secho(r["id"], fg='yellow')
            click.secho("Date : " + modified_time[0] + " " + modified_time[1].split(".")[0])
            click.secho("File : " + file_name + "\n")


@click.command('file-info', short_help="get information about file/folder")
@click.argument('fid')
def file_info(fid):
    click.secho("fetching....", fg='magenta')
    cwd = os.getcwd()
    utils.save_history([{}, fid, cwd])
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v2', http=creds.authorize(Http()))
    file_id = utils.get_fid(fid)
    t = PrettyTable(["Genreal Info", "", " "])
    t.align = "l"
    f = service.files().get(fileId=file_id).execute()
    t.add_row(["", "Name", f["title"]])
    t.add_row(["", "ID", f["id"]])
    t.add_row(["", "Mime Type", f["mimeType"]])
    t.add_row(["", "Self Link", f["selfLink"]])
    t.add_row(["", "e-tag", f["etag"]])
    date_time = f["createdDate"].split("T")
    date = date_time[0]
    time = date_time[1].split(".")[0]
    t.add_row(["", "created date", date + " " + time])
    t.add_row(["", "can edit", str(f["capabilities"]["canEdit"]) + "\n"])
    try:
        parents = service.parents().list(fileId=file_id).execute()
        if len(parents["items"]) != 0:
            t.add_row(["Parent Info", "", " "])
            for parent in parents["items"]:
                parent_name = utils.get_file(parent["id"])["name"]
                t.add_row(["", "Name", parent_name])
                t.add_row(["", "ID", parent["id"]])
                t.add_row(["", "Link", parent["parentLink"] + "\n"])
    except:
        pass
    try:
        permissions = service.permissions().list(fileId=file_id).execute()
        t.add_row(["Permissions", "", " "])
        per_num = 0
        for permission in permissions["items"]:
            per_num = per_num + 1
            if "name" in permission:
                t.add_row([per_num, "User name", permission["name"]])
                try:
                    t.add_row(["", "email address", permission["emailAddress"]])
                except KeyError:
                    t.add_row(["", "domain name", permission["domain"]])
            else:
                t.add_row([per_num, permission["id"], ""])
            t.add_row(["", "role", permission["role"]])
            t.add_row(["", "type", permission["type"] + "\n"])
    except:
        pass
    try:
        revisions = service.revisions().list(fileId=file_id).execute()
        t.add_row(["Revision", "", " "])
        rev_num = 0
        for rev in revisions["items"]:
            rev_num = rev_num + 1
            t.add_row([rev_num, "ID", rev["id"]])
            t.add_row(["", "modified by", rev["lastModifyingUser"]["displayName"]])
            t.add_row(["", "email address", rev["lastModifyingUser"]["emailAddress"]])
            date_time = rev["modifiedDate"].split("T")
            date = date_time[0]
            time = date_time[1].split(".")[0]
            t.add_row(["", "modified date", date + " " + time])
            t.add_row(["", "file size", rev["fileSize"] + "\n"])
    except:
        pass
    t.set_style(MSWORD_FRIENDLY)
    print(t)


@click.command('ignore', short_help="never track the listed local file and folders of current working directory")
@click.argument('unttrack_file', nargs=-1)
@click.option('-l', is_flag=bool, help="list out all the untracked files")
def drive_ignore(unttrack_file, l):
    cwd = os.getcwd()
    drive_ignore_path = os.path.join(cwd, '.driveignore')
    if(len(unttrack_file) != 0):
        try:
            file = open(drive_ignore_path, 'r')
            files = file.readlines()
            file.close()
        except:
            files = []
        file = open(drive_ignore_path, 'a+')
        for f in unttrack_file:
            f = f + "\n"
            file_path = os.path.join(cwd, f[:-1])
            if os.path.exists(file_path):
                if not (f in files):
                    file.write(f)
            else:
                click.secho(f[:-1] + " doesn't exist in " + cwd, fg="red")
        file.close()

    if l:
        click.secho("listing untracked files....", fg="magenta")
        utils.save_history([{"-l": ["True"]}, " ", cwd])
        if os.path.isfile(drive_ignore_path):
            file = open(drive_ignore_path, 'r')
            untracked_files = file.read()
            click.secho(untracked_files)
            file.close()
        else:
            click.secho(".driveignore file doesn't exist in " + cwd, fg="red")
            sys.exit(0)
    else:
        utils.save_history([{"-l": [None]}, " ", cwd])
