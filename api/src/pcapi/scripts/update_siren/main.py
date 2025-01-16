import argparse

from pcapi.core.history import api as history_api
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.siren import is_valid_siren


def update_siren(offerer_id: int, old_siren: str, new_siren: str, do_update: bool) -> None:
    offerer = offerers_models.Offerer.query.filter(
        offerers_models.Offerer.id == offerer_id,
        offerers_models.Offerer.siren == old_siren,
    ).one()

    print("offerer.name: ", offerer.name)

    offerer.siren = new_siren
    offerer.tags = [tag for tag in offerer.tags if tag.name != "siren-caduc"]
    db.session.add(offerer)

    history_api.add_action(
        history_models.ActionType.INFO_MODIFIED,
        author=None,
        offerer=offerer,
        modified_info={"siren": {"old_info": old_siren, "new_info": new_siren}, "tags": {"old_info": "SIREN caduc"}},
        comment="(PC-34018) SIREN modifié sur demande Partenaires Nationaux avec l'accord homologation et conformité. "
        "L'acteur culturel n'a ni établissement, ni compte bancaire et ses offres ne sont pas remboursables.",
    )

    db.session.flush()

    if do_update:
        db.session.commit()
    else:
        db.session.rollback()


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    parser = argparse.ArgumentParser(description="Update SIREN")
    parser.add_argument("--not-dry", action="store_true", help="set to really process (dry-run by default)")
    parser.add_argument("--offerer-id", help="Offerer ID")
    parser.add_argument("--old-siren", help="Old SIREN, to check consistency with --offerer-id")
    parser.add_argument("--new-siren", help="New SIREN")
    args = parser.parse_args()

    assert is_valid_siren(args.old_siren)
    assert is_valid_siren(args.new_siren)

    update_siren(int(args.offerer_id), args.old_siren, args.new_siren, args.not_dry)
