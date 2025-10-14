import statistics
import time
import typing
from typing import Iterable

import sqlalchemy.orm as sa_orm
from sqlalchemy import select

from pcapi.core.offerers import models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.utils.chunks import get_chunks


def elapsed_tims_ms(func: typing.Callable) -> typing.Callable:
    def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        start = time.time()
        res = list(func(*args, **kwargs))

        exec_time = (time.time() - start) * 1_000
        print(f"[{func.__name__}][{args[0].id}] took {exec_time}ms")
        return res, func.__name__, exec_time
    return wrapper


def get_venue_other_offerer_addresses_ids(venue: models.Venue) -> Iterable[int]:
    """Get a venue's offerer address, other than its own

    This function returns nothing if a venue has an offerer address
    shared by each of its offers.

    If a venue's offers have other (offerer) addresses, this function
    function will return them (but not the venue's offerer address).
    """
    return (
        select(offers_models.Offer.offererAddressId.distinct())
        .filter(offers_models.Offer.offererAddressId != venue.offererAddressId)
        .filter(offers_models.Offer.venueId == venue.id)
    )


@elapsed_tims_ms
def get_venue_offerer_addresses(venue: models.Venue) -> Iterable[models.OffererAddress]:
    """Find venue's offerer addresses (with addresses loaded)"""
    # TODO(jbaudet-10/2025): remove/rewriter this whole function when
    # venues are linked to addresses.
    return (
        db.session.query(models.OffererAddress)
        .filter(
            models.OffererAddress.id.in_(
                # to avoid a too heavy db scan/filtering, start by finding
                # the venue's other (offerer) addresses (not its own).
                # -> since there is no link (for now) between a venue and an
                # offerer address (as the name suggests), its addresses can
                # be found within its offers... which could mean searching
                # through a lot of them. So the better the filter, the
                # quicker the query should be.
                get_venue_other_offerer_addresses_ids(venue).union(
                    select(models.Venue.offererAddressId).filter(models.Venue.id == venue.id)
                )
            )
        )
        .options(sa_orm.joinedload(models.OffererAddress.address))
    )


@elapsed_tims_ms
def get_venue_offerer_addresses_alt(venue: models.Venue) -> Iterable[models.OffererAddress]:
    return (
        db.session.query(models.OffererAddress)
        .filter(
            models.OffererAddress.id.in_(
                select(offers_models.Offer.offererAddressId.distinct()).filter(offers_models.Offer.venueId == venue.id)
            )
        )
        .options(sa_orm.joinedload(models.OffererAddress.address))
    )


@elapsed_tims_ms
def get_venue_offerer_addresses_with_low_limit(venue: models.Venue) -> Iterable[models.OffererAddress]:
    """Find venue's offerer addresses (with addresses loaded)"""
    # TODO(jbaudet-10/2025): remove/rewriter this whole function when
    # venues are linked to addresses.
    return (
        db.session.query(models.OffererAddress)
        .filter(
            models.OffererAddress.id.in_(
                # to avoid a too heavy db scan/filtering, start by finding
                # the venue's other (offerer) addresses (not its own).
                # -> since there is no link (for now) between a venue and an
                # offerer address (as the name suggests), its addresses can
                # be found within its offers... which could mean searching
                # through a lot of them. So the better the filter, the
                # quicker the query should be.
                get_venue_other_offerer_addresses_ids(venue).union(
                    select(models.Venue.offererAddressId).filter(models.Venue.id == venue.id)
                )
            )
        )
        .options(sa_orm.joinedload(models.OffererAddress.address))
        .limit(25)
    )


@elapsed_tims_ms
def get_venue_offerer_addresses_alt_with_low_limit(venue: models.Venue) -> Iterable[models.OffererAddress]:
    return (
        db.session.query(models.OffererAddress)
        .filter(
            models.OffererAddress.id.in_(
                select(offers_models.Offer.offererAddressId.distinct()).filter(offers_models.Offer.venueId == venue.id)
            )
        )
        .options(sa_orm.joinedload(models.OffererAddress.address))
    ).limit(25)


def compute_mean_exec_time(funcs: typing.Collection, venues: typing.Collection) -> dict:
    stats = {}

    chunks = list(get_chunks(venues, len(funcs)))[:len(funcs)]
    funcs_cycle = [funcs[idx:] + funcs[:idx] for idx in range(len(funcs))]

    for venues_chunk, funcs_chunk in zip(chunks, funcs_cycle):
        for f in funcs_chunk:
            res = [f(venue) for venue in venues_chunk]

            times = [x[2] for x in res]
            name = res[0][1]

            try:
                stats[name]['times'].extend(times)
            except KeyError:
                stats[name] = {'times': times}

    return {
        name: {
            'mean': statistics.mean(stats[name]['times']),
            'median': statistics.median(stats[name]['times']),
            'min': min(stats[name]['times']),
            'max': max(stats[name]['times']),
        } for name in stats.keys()
    }


def compute_all_mean_exec_times(venues: typing.Collection) -> dict:
    return compute_mean_exec_time([
        get_venue_offerer_addresses_alt,
        get_venue_offerer_addresses_alt_with_low_limit,
        get_venue_offerer_addresses,
        get_venue_offerer_addresses_with_low_limit,
    ], venues)
