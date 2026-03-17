import click

import requests

from common import get_base_url, get_access_token


@click.group()
def api():
    """CLI for API"""
    pass


@api.command()
def health():
    """Get the health status of the pcapi instance"""
    url = get_base_url()
    click.echo(f'Check the health status of the pcapi instance with URL=`{url}`')

    health_url = f"{url}/health/api"

    try:
        response = requests.get(health_url, timeout=5)

        click.echo(f"Request to: {health_url}")
        click.echo(f"Status code: {response.status_code}")

        if response.ok:
            click.echo("Instance is healthy ✅")

            version = response.text
            click.echo(f"Current version of the instance is `{version}`")
        else:
            click.echo("Instance is NOT healthy ❌")

    except requests.exceptions.RequestException as e:
        click.echo(f"Request failed: {e}", err=True)


@api.command('me')
def describe_me():
    """Get the health status of the pcapi instance"""
    url = get_base_url()
    access_token = get_access_token()

    click.echo(f'Describe current user')

    full_url = f"{url}/native/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    try:
        response = requests.get(full_url, timeout=5, headers=headers)

        click.echo(f"Request to: {full_url}")
        click.echo(f"Status code: {response.status_code}")

        data = response.json()
        if response.ok:
            click.echo("Describe user using me route succeeded ✅")
            click.echo(f"User details: {data}")

        else:
            click.echo("Signin failed")
            click.echo(f"Response: {data}")

    except requests.exceptions.RequestException as e:
        click.echo(f"Request failed: {e}", err=True)
