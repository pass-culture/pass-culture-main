import os

import click


def get_base_url():
    base_url = os.environ.get("PCAPI_BASE_URL")
    if not base_url:
        base_url = "https://backend.testing.passculture.team"
        click.echo("PCAPI_BASE_URL environment variable is not set. So default value will be used")
        click.echo(f"Default value is `{base_url}`")

    return base_url


def get_access_token():
    access_token = os.environ.get("ACCESS_TOKEN")
    if not access_token:
        raise click.ClickException("ACCESS_TOKEN environment variable is not set")

    return access_token
