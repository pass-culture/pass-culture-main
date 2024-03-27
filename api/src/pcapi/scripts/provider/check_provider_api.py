import datetime
import time

import click

from pcapi.infrastructure.repository.stock_provider.provider_api import ProviderAPI
from pcapi.local_providers.provider_api import synchronize_provider_api
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("check_provider_api")
@click.option("--url", required=True, help="Endpoint url")
@click.option("--siret", required=True, help="A working siret")
@click.option("--token", required=False, default=None, help="(Optional) Basic authentication token")
def check_provider_api(url: str, siret: str, token: str | None) -> None:
    provider_api = ProviderAPI(
        api_url=url,
        name="TestApi",
        authentication_token=token,
    )

    assert provider_api.is_siret_registered(siret), "L'appel avec uniquement le siret dans l'url doit fonctionner"

    stocks: dict[str, str] = provider_api.stocks(siret, limit=1)
    stocks_total = stocks.get("total")
    assert stocks_total is not None, "Le total est manquant."
    assert int(stocks_total) > 0, "Le total n'est pas strictement supérieur à 0."

    assert "stocks" in stocks, 'La clé "stocks" est manquante.'
    stock = stocks["stocks"][0]
    assert isinstance(stock, dict), "Chaque stock devrait être un objet (dictionnaire)."
    assert "ref" in stock, 'Chaque stock devrait avoir une clé "ref".'
    assert "available" in stock, 'Chaque stock devrait avoir une clé "available".'

    two_stocks = provider_api.stocks(siret, limit=2)
    assert (
        len(stocks.get("stocks")) == 1 and len(two_stocks.get("stocks")) == 2
    ), "Le limit doit limiter le nombre de résultat"

    next_stock = provider_api.stocks(siret, limit=1, last_processed_reference=stocks.get("stocks")[0]["ref"])
    assert (
        next_stock.get("stocks")[0]["ref"] == two_stocks.get("stocks")[1]["ref"]
    ), "Le after doit correctement décaller les résultats"
    assert int(stocks.get("total")) == int(next_stock.get("total")), "Le after ne doit pas impacter le total"

    no_stocks = provider_api.stocks(
        siret,
        limit=1,
        modified_since=datetime.datetime.strftime(datetime.datetime.now(datetime.timezone.utc), "%Y-%m-%dT%H:%M:%SZ"),
    )
    modified_since_is_implemented = int(stocks.get("total")) > int(no_stocks.get("total"))

    stock_count = 0
    batch_count = 0
    start_time = time.time()
    for raw_stocks in synchronize_provider_api._get_stocks_by_batch(siret, provider_api, None):
        stock_count += len(raw_stocks)
        batch_count += 1
    duration = time.time() - start_time
    average_duration = duration / batch_count

    print(
        "C'est ok !"
        "\n\n"
        f"Le différentiel est implémenté : {modified_since_is_implemented}"
        "\n\n"
        f"Le format des stocks ressemble à {stock}"
        "\n\n"
        f"Récupérer {stock_count} offres en {batch_count} fois"
        "\n\n"
        f"a duré {duration} secondes."
        "\n\n"
        f"Cela fait {average_duration}s par requête."
    )
