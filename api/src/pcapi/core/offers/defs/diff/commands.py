from collections import Counter

from pcapi.core.categories import subcategories
from pcapi.core.offers.defs import utils
from pcapi.utils.blueprint import Blueprint

from . import api


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("check_subcategories_extra_data")
def check_subcategories_extra_data() -> None:
    """Check that all new models' extra data are the expected ones

    For each known subcategory, find its related (new) model and check
    that the extra data matches its conditional fields.
    """
    whole_diff_status = [
        api.build_model_and_subcategory_fields_diff_status(utils.MODELS[subcategory.id], subcategory)
        for subcategory in subcategories.ALL_SUBCATEGORIES
    ]

    for status in whole_diff_status:
        print(f"[{status.kind}] {status.subcategory_id}")

        if status.kind != "no_diff":
            print(f"  >>> diff: {status.diff}")

    summary = Counter([diff.kind for diff in whole_diff_status])
    print("\nSummary")
    for kind, total in summary.items():
        print(f"  {kind}: {total}")


@blueprint.cli.command("check_no_subcategory_is_missing")
def check_no_subcategory_is_missing() -> None:
    """Check that each known subcategory has its own new model"""
    known_subcategory_ids = {sub.id for sub in subcategories.ALL_SUBCATEGORIES}
    found_model_subcategory_ids = set(utils.MODELS.keys())

    missing_subcategory_ids = known_subcategory_ids - found_model_subcategory_ids
    unexpected_subcategory_ids = found_model_subcategory_ids - known_subcategory_ids

    if missing_subcategory_ids:
        print(f"Found missing subcategoy ids: {missing_subcategory_ids}")
    elif unexpected_subcategory_ids:
        print(f"Found unexpected subcategoy ids: {unexpected_subcategory_ids}")
    else:
        print("No error found")


@blueprint.cli.command("check_all_typologies_are_equal")
def check_all_typologies_are_equal() -> None:
    """Check that all typologies (is_digital/is_event/is_selectable) are equal"""
    whole_diff_status = {
        subcategory.id: api.build_typology_diff(subcategory, utils.MODELS[subcategory.id])
        for subcategory in subcategories.ALL_SUBCATEGORIES
    }

    errors_count = 0
    for subcategory_id, diff in whole_diff_status.items():
        print(f"[{diff}] {subcategory_id}")

        if diff != "same":
            errors_count += 1

    print(f"\n> errors count: {errors_count}")
