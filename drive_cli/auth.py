from . import utils
import os
import click
import pyfiglet
import requests
import sys
from oauth2client import file, client, tools
from pathlib import Path

SCOPES = 'https://www.googleapis.com/auth/drive'
dirpath = os.path.dirname(os.path.realpath(__file__))
config_path = Path.home().joinpath(".config", "drive-cli")

@click.command("login",
    help='Log in to your google account and authenticate the service. See README for more detailed instructions '
         'regarding authorization.')
@click.option("--remote",
    is_flag=True,
    default=False,
    help="Remote login in case browser is on a different machine")
@click.option("--json-file",
    type=click.Path(exists=True),
    default=None,
    help="Specify the location of your oauth token json file.")
def login(remote=False, json_file=None):
    flags = tools.argparser.parse_args(args=[])
    if remote:
        flags.noauth_local_webserver = True
        click.secho("Running without local webserver auth.")
    if json_file:
        click.secho("Using Oauth JSON file {}".format(json_file))
    token = config_path.joinpath('token.json')
    store = file.Storage(str(token))
    creds = store.get() if token.is_file() else None
    if not creds or creds.invalid:
        client_id = json_file or config_path.joinpath('oauth.json')
        if client_id.is_file():
            store = file.Storage(str(token))
            flow = client.flow_from_clientsecrets(str(client_id), SCOPES)
            creds = tools.run_flow(flow, store, flags)
            store.put(creds)
        else:
            click.secho("Unable to find your oauth json file. Please re-run, specifying the JSON file with"
                        "'drive login --json-file /path/to/your/file.json'", fg="red")
            sys.exit(1)

    click.secho(
        "********************** welcome to **********************", bold=True, fg='red')
    result = pyfiglet.figlet_format("Drive - CLI", font="slant")
    click.secho(result, fg='yellow')
    click.secho(
        "********************************************************", bold=True, fg='red')


def loggin():
    drive = utils.Drive()
    cwd = os.getcwd()
    drive.save_history([{}, "", cwd])


@click.command('logout', short_help='logout from the account logged in with')
def logout():
    '''
    logout: logout from the account that has been logged in
    '''
    drive = utils.Drive()
    cwd = os.getcwd()
    drive.save_history([{}, "", cwd])
    token = config_path.joinpath('token.json')
    if not token.is_file():
        click.secho("You are not logged in", fg="red")
        sys.exit(1)
    else:
        store = file.Storage(token)
        creds = store.get()
        if creds:
            requests.post('https://accounts.google.com/o/oauth2/revoke',
                          params={'token': creds.access_token},
                          headers={'content-type': 'application/x-www-form-urlencoded'})
        os.remove(str(token))
        click.secho("Logged Out successfully\nUse:")
        click.secho("drive login", bold=True, fg='green')
        click.secho("to login again")
