#!/usr/bin/env python3
import json
import os
import click
import requests


def _get_oauth_client(hostname):
  """Get the OAuth client ID and secret."""
  url = f'https://{hostname}/api/v1/oauth-clients/local'
  try:
    response = requests.get(url, headers={
      'Accept': 'application/json'
    })
    response.raise_for_status()
    data = response.json()

    client_id = data.get('client_id')
    client_secret = data.get('client_secret')
    click.echo(click.style(f"Fetched client ID {client_id} and secret {client_secret}", fg='green'))
    return client_id, client_secret
  except requests.exceptions.RequestException as e:
    click.echo(click.style(f"Error: {e}", fg='red'))
    exit(1)


def _issue_auth_token(hostname, client_id, client_secret, username, password):
  """Issue access token via the OAuth client."""
  url = f'https://{hostname}/api/v1/users/token'
  response = requests.post(url, {
    'client_id': client_id,
    'client_secret': client_secret,
    'grant_type': 'password',
    'response_type': 'code',
    'username': username,
    'password': password
  }, headers={
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'application/json'
  })
  if response.status_code == 200:
    data = response.json()
    click.echo(click.style(f"Issued token {data.get('access_token')}", fg='green'))
    return data
  else:
    click.echo(click.style(f"Error code {response.status_code}: {response.text}", fg='red'))
    exit(2)


@click.command()
@click.argument('hostname')
@click.argument('username')
@click.argument('password')
def issue_auth_token(hostname, username, password):
  """Issue auth tokens for a PeerTube site."""

  os.makedirs('data', exist_ok=True)

  client_id, client_secret = _get_oauth_client(hostname)
  bearer_token = _issue_auth_token(hostname, client_id, client_secret, username, password)
  token_file_path = 'data/auth-bearer-token.json'
  with open(token_file_path, 'w') as auth_token_file:
    auth_token_file.write(json.dumps(bearer_token, indent=2))
  click.echo(click.style(f"Auth token written to {token_file_path}: "
                         f"{bearer_token['access_token']}", fg='green'))


if __name__ == '__main__':
  issue_auth_token()
