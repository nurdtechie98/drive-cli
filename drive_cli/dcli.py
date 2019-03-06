import os
import sys
import click

dirpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirpath)
import auth
import actions


@click.group()
@click.option('--remote', is_flag=True, default=False, help='remote login in case browser is on a different machine')
def cli(remote):
    auth.LOGIN(remote)

cli.add_command(auth.Login)

cli.add_command(actions.view_file)

@cli.command('clone', short_help='download any file using sharing link or file ID it will be automatically tracked henceforth')
@click.argument('payload')
def download(payload):
    '''
    clone: download a file/folder  using either the sharing link or using the file ID  for the file
    '''
    if payload != None:
        fid = get_fid(payload)
    else:
        click.secho("argument error", fg='red')
        with click.Context(download) as ctx:
            click.echo(download.get_help(ctx))
        sys.exit(0)
    clone = get_file(fid)
    cwd = os.getcwd()
    click.secho("cloning into '" + clone['name'] + "' .....", fg='magenta')
    if clone['mimeType'] == 'application/vnd.google-apps.folder':
        new_dir = os.path.join(cwd, clone['name'])
        create_new(new_dir, fid)
        pull_content(new_dir, fid)
    else:
        file_download(clone, cwd)
    click.secho("cloning of " + clone['name'] + ' completed', fg='green')


@cli.command('add_remote', short_help='upload any existing file to drive')
@click.option('--file', help='specify the partcular file to uploaded else entire directory is uploaded')
@click.option('--pid', help='specify particular folder id/sharing_link of the folder under which remote must must be added')
def create_remote(file, pid):
    """
    add_remote: create remote equivalent for existing file/folder in local device
    """
    cwd = os.getcwd()
    if pid == None:
        pid = 'root'
    if file != None:
        file_path = os.path.join(cwd, file)
        if os.path.isfile(file_path):
            upload_file(file, file_path, pid)
        else:
            click.secho("No such file exist: " + file_path, fg="red")
            with click.Context(create_remote) as ctx:
                click.echo(create_remote.get_help(ctx))
    else:
        sep = os.sep
        dir_cd, name = sep.join(cwd.split(sep)[:-1]), cwd.split(sep)[-1]
        child_cwd, child_id = create_dir(dir_cd, pid, name)
        push_content(child_cwd, child_id)
    if pid != None:
        parent_file = get_file(pid)
        parent_name = parent_file['name']
        click.secho("content added under directory " +
                    parent_name, fg='magenta')


@cli.command('rm', short_help='delete a particular file in drive')
@click.option('--file', help='specify the partcular file to deleted else entire directory is deleted')
@click.option('--id', help='delete untracked file directly using id or sharing link, can be used even for unlinked files')
def delete(file, id):
    '''
    rm: delete a particular file/folder from the directory in the remote drive
    '''
    cwd = os.getcwd()
    if id == None:
        if file != None:
            file_path = os.path.join(cwd, file)
            if os.path.isfile(file_path):
                local_dir = get_child(cwd)
                fid = local_dir[file]
            else:
                click.secho("No such file exist: " + file_path, fg="red")
                with click.Context(delete) as ctx:
                    click.echo(delete.get_help(ctx))
            cwd = file_path
        else:
            data = drive_data()
            fid = data[cwd]
            data.pop(cwd, None)
            drive_data(data)
        delete_file(fid)
    else:
        fid = get_fid(id)
        delete_file(fid)


@cli.command('ls', short_help='list out all the files present in this directory in the drive for tracked directories')
def list_out():
    """
    ls: Print files belonging to a folder in the drive folder of the current directory
    """
    data = drive_data()
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    service = build('drive', 'v3', http=creds.authorize(Http()))
    page_token = None
    lis = []
    cwd = os.getcwd()
    if cwd not in data.keys():
        click.secho(
            "following directory has not been tracked: \nuse drive add_remote or drive clone", fg='red')
        sys.exit(0)
    query = "'" + data[cwd]['id'] + "' in parents"
    # print(query)
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


@cli.command('cat', short_help='view contents of the file using its file id or sharing link')
@click.argument('link')
def view(link):
    fid = get_fid(link)
    concat(fid)


@cli.command('status', short_help='list changes committed since last sync')
def status():
    '''
    status: get a change log of files changed since you had the last sync(push/pull/clone)
    '''
    cwd = os.getcwd()
    data = drive_data()
    if cwd not in data.keys():
        click.secho(
            "following directory has not been tracked: \nuse drive add_remote or drive clone ", fg='red')
        sys.exit(0)
    sync_time = data[cwd]['time']
    list_status(cwd, sync_time)


@cli.command('pull', short_help='get latest updates from online drive of the file')
def pull():
    data = drive_data()
    cwd = os.getcwd()
    if cwd not in data.keys():
        click.secho(
            "following directory has not been tracked: \nuse drive add_remote or drive clone ", fg='red')
        sys.exit(0)
    fid = data[cwd]['id']
    syn_time = data[cwd]['time']
    current_root = get_file(fid)
    click.secho("checking for changes in '" +
                current_root['name'] + "' ....", fg='magenta')
    pull_content(cwd, fid)
    click.secho(current_root['name'] +
                " is up to date with drive", fg='yellow')


@cli.command('push', short_help='push modification from local files to the drive')
def push():
    '''
    push the latest changes from your local folder that has been added/cloned to google drive.
    '''
    data = drive_data()
    cwd = os.getcwd()
    if cwd not in data.keys():
        click.secho(
            "following directory has not been tracked: \nuse drive add_remote or drive clone ", fg='red')
        sys.exit(0)
    fid = data[cwd]['id']
    syn_time = data[cwd]['time']
    current_root = get_file(fid)  # can be avoided
    click.secho("checking for changes in '" +
                current_root['name'] + "' ....", fg='magenta')
    push_content(cwd, fid)
    click.secho("Working directory is clean", fg="green")

cli.add_command(auth.logout)


if __name__ == '__main__':
    pass
