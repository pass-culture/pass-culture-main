from concurrent.futures import ThreadPoolExecutor, as_completed

import click

import requests

from common import get_base_url, get_access_token


@click.group()
def native():
    """CLI for native"""
    pass


@native.command('list-offer')
@click.option('--offer-id','-id',  help='Id of the offer', type=str, multiple=True, default=2748)
@click.option('--number-of-requests', '-n', help='Number of requests', type=int, default=10,)
@click.option('--concurrent', '-c', help='Number of concurrent threads', type=int, default=2,)
@click.option('--timeout', '-t', help='HTTP request timeout', type=int, default=5,)
def offer(offer_id, number_of_requests, concurrent, timeout):
    """Get offer stocks concurrently
    Use offer id: 1520
    python main.py offer -id 1520 -n 10 -c 2
    """
    url = get_base_url()
    click.echo(f'Describe offers to the pcapi instance with URL=`{url}`')
    full_url = f"{url}/native/v2/offers/stocks"

    payload = {"offer_ids": list(offer_id)}
    click.echo(f"Request to: {full_url}")
    click.echo(f"With payload: {payload}")

    def do_offer():
        try:
            response = requests.post(full_url, timeout=timeout, json=payload)
            return response.status_code, response.json() if response.content else None
        except requests.exceptions.RequestException as e:
            return None, str(e)

    results = []
    success_count = 0
    failed_count = 0
    with ThreadPoolExecutor(max_workers=concurrent) as executor:
        futures = [executor.submit(do_offer) for _ in range(number_of_requests)]
        for future in as_completed(futures):
            status, data = future.result()
            results.append((status, data))
            click.echo(f"Status code: {status}")
            if status == 200:
                success_count += 1
                click.echo(f"Got {len(data['offers'])} offers ✅")
            else:
                failed_count += 1
                click.echo(f"Offer request failed: {data}")

    click.echo(f"Total requests: {len(results)}")
    click.echo(f"Successful requests: {success_count} / {len(results)}")
    click.echo(f"Failed requests: {failed_count} / {len(results)}")
