from collections import Counter

from pcapi.core.categories import subcategories
from pcapi.core.offers.services import utils
from pcapi.utils.blueprint import Blueprint

from .api import build_subcategories_diff_status


blueprint = Blueprint(__name__, __name__)


@blueprint.cli.command("check_subcategories_extra_data")
def check_subcategories_extra_data() -> None:
    """Check that each new model maps known extra data as expected

    For each known subcategory, print the current diff status: does
    the new model's extra_data field maps all its fields as expected?
    """
    status = build_subcategories_diff_status()
    for diff in status:
        print(f"[{diff.subcategory_id}]")
        print(f"  kind: {diff.kind}")

        if diff.kind != "no_diff":
            print(f"  diff: {diff.diff}")

    summary = Counter([diff.kind for diff in status])
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
