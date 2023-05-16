#!/usr/bin/env python3

import os
import json
import click
import requests

AUTH_ENDPOINT = 'https://pulp.swm.cc/users/tokens/sign_in'
SEARCH_ENDPOINT = 'https://pulp.swm.cc/api/v1/links/search'
AUTH_TOKEN_FILE = '/tmp/pulp_auth_token.txt'


def get_auth_token():
    if os.path.exists(AUTH_TOKEN_FILE):
        with open(AUTH_TOKEN_FILE, 'r') as f:
            auth_token = f.read().strip()
            if validate_auth_token(auth_token):
                return auth_token

    email = os.getenv('PULP_USERNAME')
    password = os.getenv('PULP_PASSWORD')

    response = requests.post(AUTH_ENDPOINT, json={'email': email, 'password': password})

    if response.status_code == 200:
        auth_token = response.json()['token']
        with open(AUTH_TOKEN_FILE, 'w') as f:
            f.write(auth_token)
        return auth_token

    return None


def validate_auth_token(auth_token):
    headers = {'Authentication': auth_token}
    response = requests.get(SEARCH_ENDPOINT, headers=headers)
    return response.status_code == 200


@click.command()
@click.option('-s', '--search', help='Search term')
def search_command(search):
    auth_token = get_auth_token()

    if auth_token:
        headers = {'Authentication': auth_token}
        params = {'term': search}
        response = requests.get(SEARCH_ENDPOINT, headers=headers, params=params)

        if response.status_code == 200:
            result = response.json()
            links = json.dumps(result, indent=4, sort_keys=True)
            decoded_results = json.loads(links)
            for link in decoded_results:
                click.echo(link['title'] + "  -  " + link['page'])
        else:
            click.echo(f'Error: {response.status_code}')
    else:
        click.echo('Authorisation failed')


if __name__ == '__main__':
    search_command()
