from pcapi.core import search
import pcapi.core.educational.api as educational_api
import pcapi.core.offers.api as offers_api
from pcapi.scheduled_tasks.decorators import log_cron_with_transaction
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("index_offers_in_algolia_by_offer")
@log_cron_with_transaction
def index_offers_in_algolia_by_offer():  # type: ignore [no-untyped-def]
    """Pop offers from indexation queue and reindex them."""
    search.index_offers_in_queue()


@blueprint.cli.command("index_offers_in_algolia_by_venue")
@log_cron_with_transaction
def index_offers_in_algolia_by_venue():  # type: ignore [no-untyped-def]
    """Pop venues from indexation queue and reindex their offers."""
    search.index_offers_of_venues_in_queue()


@blueprint.cli.command("index_collective_offers")
@log_cron_with_transaction
def index_collective_offers():  # type: ignore [no-untyped-def]
    """Pop collective offers from indexation queue and reindex them."""
    search.index_collective_offers_in_queue()


@blueprint.cli.command("index_collective_offer_templates")
@log_cron_with_transaction
def index_collective_offer_templates():  # type: ignore [no-untyped-def]
    """Pop collective offers template from indexation queue and reindex them."""
    search.index_collective_offers_templates_in_queue()


@blueprint.cli.command("delete_expired_offers_in_algolia")
@log_cron_with_transaction
def delete_expired_offers_in_algolia():  # type: ignore [no-untyped-def]
    """Unindex offers that have expired.

    By default, process offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included)."""
    offers_api.unindex_expired_offers()


@blueprint.cli.command("delete_expired_collective_offers_in_algolia")
@log_cron_with_transaction
def delete_expired_collective_offers_in_algolia():  # type: ignore [no-untyped-def]
    """Unindex collective offers that have expired.

    By default, process collective offers that have expired within the last 2
    days. For example, if run on Thursday (whatever the time), this
    function handles collective offers that have expired between Tuesday 00:00
    and Wednesday 23:59 (included)."""
    educational_api.unindex_expired_collective_offers()


@blueprint.cli.command("index_offers_in_error_in_algolia_by_offer")
@log_cron_with_transaction
def index_offers_in_error_in_algolia_by_offer():  # type: ignore [no-untyped-def]
    """Pop offers from the error queue and reindex them."""
    search.index_offers_in_queue(from_error_queue=True)


@blueprint.cli.command("index_collective_offers_in_error")
@log_cron_with_transaction
def index_collective_offers_in_error():  # type: ignore [no-untyped-def]
    """Pop collective offers from the error queue and reindex them."""
    search.index_collective_offers_in_queue(from_error_queue=True)


@blueprint.cli.command("index_collective_offers_templates_in_error")
@log_cron_with_transaction
def index_collective_offers_templates_in_error():  # type: ignore [no-untyped-def]
    """Pop collective offers template from the error queue and reindex them."""
    search.index_collective_offers_templates_in_queue(from_error_queue=True)


@blueprint.cli.command("index_venues")
@log_cron_with_transaction
def index_venues():  # type: ignore [no-untyped-def]
    """Pop venues from indexation queue and reindex them."""
    search.index_venues_in_queue()


@blueprint.cli.command("index_venues_in_error")
@log_cron_with_transaction
def index_venues_in_error():  # type: ignore [no-untyped-def]
    """Pop venues from the error queue and reindex them."""
    search.index_venues_in_queue(from_error_queue=True)
