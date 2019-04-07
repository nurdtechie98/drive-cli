from . import utils
import os
import click
import pyfiglet
import requests
from oauth2client import file, client, tools

SCOPES = 'https://www.googleapis.com/auth/drive'
dirpath = os.path.dirname(os.path.realpath(__file__))


def login(remote):
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    if not creds or creds.invalid:
        client_id = os.path.join(dirpath, 'oauth.json')
        flow = client.flow_from_clientsecrets(client_id, SCOPES)
        flags = tools.argparser.parse_args(args=[])
        if remote:
            flags.noauth_local_webserver = True
        creds = tools.run_flow(flow, store, flags)
        click.secho(
            "********************** welcome to **********************", bold=True, fg='red')
        result = pyfiglet.figlet_format("Drive - CLI", font="slant")
        click.secho(result, fg='yellow')
        click.secho(
            "********************************************************", bold=True, fg='red')


@click.command('login', short_help='login to your google account and authenticate the service')
def loggin():
    cwd = os.getcwd()
    utils.save_history([{}, "", cwd])


@click.command('logout', short_help='logout from the account logged in with')
def logout():
    '''
    logout: logout from the account that has been logged in
    '''
    cwd = os.getcwd()
    utils.save_history([{}, "", cwd])
    token = os.path.join(dirpath, 'token.json')
    store = file.Storage(token)
    creds = store.get()
    if creds:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
                      params={'token': creds.access_token},
                      headers={'content-type': 'application/x-www-form-urlencoded'})

    os.remove(token)
    click.secho("Logged Out successfully\nUse:")
    click.secho("drive login", bold=True, fg='green')
    click.secho("to login again")
