import collections
import datetime
import enum
import itertools
import logging
import re
import typing

from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offerers import factories as offerers_factories


LOGGER = logging.getLogger(__name__)
FIELD_RE = re.compile(r"(?:(?P<model>\w+)__)?(?P<field>\w+)")


class WeekDays(enum.IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


def get_next_weekday_after_given_delay_from_reference(
    reference_date: datetime.datetime,
    expected_weekday: int,
    exclusion_delay: datetime.timedelta,
):
    next_weekday = reference_date + datetime.timedelta(days=expected_weekday - reference_date.weekday())
    while next_weekday - reference_date <= exclusion_delay:
        next_weekday += datetime.timedelta(7)
    return next_weekday


NOW = datetime.datetime.utcnow()
YESTERDAY = NOW - datetime.timedelta(days=1)
TOMORROW = NOW + datetime.timedelta(days=1)
CANCELLATION_DELAY = datetime.timedelta(hours=48)
NEXT_MONDAY_AFTER_48H = get_next_weekday_after_given_delay_from_reference(
    NOW, WeekDays.MONDAY.value, CANCELLATION_DELAY
)
NEXT_SATURDAY_AFTER_48H = get_next_weekday_after_given_delay_from_reference(
    NOW, WeekDays.SATURDAY.value, CANCELLATION_DELAY
)

SPECS = [
    {
        "subcategories": tuple(subcategories.EVENT_SUBCATEGORIES.values()),
        "cases": {
            "RESERVATION DATE DEMAIN NON ANNULABLE": {
                "stock__beginningDatetime": TOMORROW,
            },
            "RESERVATION DATE SEMAINE ANNULABLE": {
                "stock__beginningDatetime": NEXT_MONDAY_AFTER_48H,
            },
            "RESERVATION DATE WEEKEND ANNULABLE": {
                "stock__beginningDatetime": NEXT_SATURDAY_AFTER_48H,
            },
            "RESERVATION OFFRE SIMPLE": {
                "isDuo": False,
            },
            "RESERVATION OFFRE DUO": {
                "isDuo": True,
            },
        },
    },
    {
        "subcategories": tuple(subcategories.EXPIRABLE_SUBCATEGORIES.values()),
        "cases": {
            "RESERVATION IMPOSSIBLE OFFRE EXPIREE": {
                "stock__beginningDatetime": YESTERDAY,
            },
        },
    },
    {
        "subcategories": tuple(subcategories.ALL_SUBCATEGORIES),
        "cases": {
            "RESERVATION IMPOSSIBLE OFFRE EPUISEE": {
                "stock__quantity": 0,
            },
            "RESERVATION JEUNE GRATUITE": {
                "stock__price": 0,
            },
            "RESERVATION BENEFICAIRE PAYANTE": {
                "stock__price": 35,
            },
        }
    },
    {
        "subcategories": tuple(subcategories.PHYSICAL_SUBCATEGORIES.values()),
        "cases": {
            "RESERVATION OFFRE PHYSIQUE": {},
        }
    },
    {
        "subcategories": tuple(subcategories.DIGITAL_SUBCATEGORIES.values()),
        "cases": {
            "RESERVATION OFFRE NUMERIQUE": {},
        }
    },
]

def save_e2e_sandbox() -> None:
    offerer = offerers_factories.OffererFactory(name="e2e_offerer")
    LOGGER.info("offerer %s created", offerer.name)

    permanent_venue, temp_venue = (
        offerers_factories.VenueFactory(
            name=f"e2e_{'permanent' if permanent else 'temporary'}_venue",
            isPermanent=permanent,
            managingOfferer=offerer,
        ) for permanent in (True, False)
    )
    for venue in (permanent_venue, temp_venue):
        LOGGER.info("venue %s created", venue.name)

    venue_cycler = itertools.cycle((permanent_venue, temp_venue))
    for subcategory in subcategories.ALL_SUBCATEGORIES:
        for i in range(1, 11):
            create_offers(subcategory, i, venue_cycler)


def get_cases_for_subcategory(subcategory: subcategories.Subcategory) -> dict:
    case_groups = (spec["cases"] for spec in SPECS if subcategory in spec["subcategories"])
    cases = {}
    for group in case_groups:
        cases.update(group)
    return cases


def extract_specs_by_model(cases: dict[str, dict]) -> dict[str, dict]:
    specs_by_model = collections.defaultdict(dict)
    for spec, value in cases.items():
        match = FIELD_RE.match(spec)
        assert match

        model = match.group("model") or "offer"
        field = match.group("field")

        specs_by_model[model][field] = value

    return specs_by_model


def create_offers(subcategory: subcategories.Subcategory, index: int, venues: itertools.cycle) -> None:
    cases = get_cases_for_subcategory(subcategory)

    for case_name, case_specs in cases.items():
        name = "-".join([
            subcategory.category.id,
            subcategory.id,
            "pas de public destinataire",
            case_name,
            str(index),
        ])
        specs_by_model = extract_specs_by_model(case_specs)

        offer = offers_factories.OfferFactory(
            venue=next(venues),
            name=name,
            **specs_by_model['offer'],
        )
        if specs_by_model['stock']:
            offers_factories.StockFactory(offer=offer, **specs_by_model['stock'])
        else:
            offers_factories.StockFactory(offer=offer, quantity=10)
        print(f"{name}\n\toffer: {specs_by_model['offer']}\n\tstock: {specs_by_model['stock']}")
