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

cli.add_command(actions.download)

cli.add_command(actions.create_remote)

cli.add_command(actions.delete)

cli.add_command(actions.list_out)

cli.add_command(actions.view)


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
