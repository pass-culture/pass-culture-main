from concurrent.futures import ThreadPoolExecutor, as_completed

import click
import requests

from common import get_base_url, get_access_token


@click.group()
def api():
    """CLI for API"""
    pass


@api.command()
@click.option('--number-of-requests', '-n', help='Number of requests', type=int, default=10,)
@click.option('--concurrent', '-c', help='Number of concurrent threads', type=int, default=2,)
@click.option('--timeout', '-t', help='HTTP request timeout', type=int, default=5,)
def health(number_of_requests, concurrent, timeout):
    """Get the health status of the pcapi instance"""
    url = get_base_url()
    click.echo(f'Check the health status of the pcapi instance with URL=`{url}`')

    health_url = f"{url}/health/api"

    def get_health():
        try:
            response = requests.get(health_url, timeout=timeout)
            version = response.text.split('\n')[0]
            return response.status_code, version
        except requests.exceptions.RequestException as e:
            return None, str(e)

    results = []
    success_count = 0
    failed_count = 0

    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(get_health) for _ in range(number_of_requests)]
        for future in as_completed(futures):
            status, data = future.result()
            results.append((status, data))
            click.echo(f"Status code: {status}")
            if status == 200:
                success_count += 1
                click.echo(f"API is healthy and version is `{data}` ✅")
            else:
                failed_count += 1
                click.echo(f"API health request failed: {data} ❌")

    click.echo(f"Total requests: {len(results)}")
    click.echo(f"Successful requests: {success_count} / {len(results)}")
    click.echo(f"Failed requests: {failed_count} / {len(results)}")


@api.command('me')
@click.option('--number-of-requests', '-n', help='Number of requests', type=int, default=10,)
@click.option('--concurrent', '-c', help='Number of concurrent threads', type=int, default=2,)
@click.option('--timeout', '-t', help='HTTP request timeout', type=int, default=5,)
def describe_me(number_of_requests, concurrent, timeout):
    """Get the health status of the pcapi instance"""
    url = get_base_url()
    access_token = get_access_token()

    click.echo('Describe current user')

    full_url = f"{url}/native/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}

    def get_current_user_details():
        try:
            response = requests.get(full_url, timeout=timeout, headers=headers)
            user_data = response.json()
            return response.status_code, user_data
        except requests.exceptions.RequestException as e:
            return None, str(e)

    results = []
    success_count = 0
    failed_count = 0

    # TODO: feel free to rework this
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(get_current_user_details) for _ in range(number_of_requests)]
        for future in as_completed(futures):
            status, data = future.result()
            results.append((status, data))
            click.echo(f"Status code: {status}")
            if status == 200:
                success_count += 1
                click.echo("Describe user using me route succeeded ✅")
            else:
                failed_count += 1
                click.echo(f"Describe user failed: {data} ❌")

    click.echo(f"Total requests: {len(results)}")
    click.echo(f"Successful requests: {success_count} / {len(results)}")
    click.echo(f"Failed requests: {failed_count} / {len(results)}")

