import click

import requests

from common import get_base_url


@click.group()
def signin():
    """CLI for signin"""
    pass


@signin.command()
@click.option('--url', help='Url of the instance', type=str, default="https://backend.testing.passculture.team",)
@click.option('--identifier', help='identifier of the user', type=str, required=True,)
@click.option('--password', help='Password of the user', type=str, required=True,)
@click.option('--token', help='Recaptcha token', type=str, required=True,)
def login(identifier, password, token):
    """Get the health status of the pcapi instance"""
    url = get_base_url()
    click.echo(f'Signin to the pcapi instance with URL=`{url}`')
    signin_url = f"{url}/native/v1/signin"
    payload = {"identifier": identifier, "password": password, "token": token}

    try:
        response = requests.post(signin_url, timeout=5,  json=payload)

        click.echo(f"Request to: {signin_url}")
        click.echo(f"Status code: {response.status_code}")

        data = response.json()
        if response.ok:
            click.echo("Signin succeeded ✅")
            breakpoint()

            # TODO: data should contains details related to token

        else:
            click.echo("Signin failed")
            click.echo(f"Response: {data}")

    except requests.exceptions.RequestException as e:
        click.echo(f"Request failed: {e}", err=True)
