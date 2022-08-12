import click

from pcapi.scripts.booking.delete_cancelled_booking import delete_cancelled_booking
from pcapi.utils.blueprint import Blueprint


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("delete_cancelled_booking")
@click.option("--venue-id", required=True, help="Id of the venue to delete cancelled bookings", type=int)
@click.option("--stop-on-exception", default=True, type=bool)
def delete_booking(venue_id: int, stop_on_exception: bool) -> None:
    delete_cancelled_booking(venue_id, stop_on_exception)
