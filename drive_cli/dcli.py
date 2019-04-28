from . import auth
from . import actions
import os
import sys
import click

dirpath = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dirpath)


@click.group()
@click.option('--remote', is_flag=True, default=False, help='remote login in case browser is on a different machine')
def cli(remote):
    auth.login(remote)

cli.add_command(auth.loggin)

cli.add_command(actions.view_file)

cli.add_command(actions.download)

cli.add_command(actions.create_remote)

cli.add_command(actions.delete)

cli.add_command(actions.list_out)

cli.add_command(actions.view)

cli.add_command(actions.status)

cli.add_command(actions.pull)

cli.add_command(actions.push)

cli.add_command(actions.share)

cli.add_command(actions.history)

cli.add_command(actions.get_revision)

cli.add_command(actions.file_info)

cli.add_command(actions.drive_ignore)

cli.add_command(auth.logout)

if __name__ == '__main__':
    pass
