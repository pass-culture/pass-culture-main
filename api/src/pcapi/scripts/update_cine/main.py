from pcapi.app import app
from pcapi.core.providers import models
from pcapi.models import db


def get_all_cds_ids() -> list[int]:
    return [c.id for c in db.session.query(models.CDSCinemaDetails.id)]


def get_all_boost_ids() -> list[int]:
    return [c.id for c in db.session.query(models.BoostCinemaDetails.id)]


def main() -> None:
    cds_ids = get_all_cds_ids()
    boost_ids = get_all_boost_ids()

    db.session.rollback()

    try:
        for cds_id in cds_ids:
            cds = db.session.query(models.CDSCinemaDetails).filter_by(id=cds_id).one()
            cds.cinemaApiToken = cds.cinemaApiToken
            db.session.commit()
    except Exception as e:
        print("error on cds_id %s" % cds_id)
        raise e

    try:
        for boost_id in boost_ids:
            boost = db.session.query(models.BoostCinemaDetails).filter_by(id=boost_id).one()
            boost.token = boost.token
            db.session.commit()
    except Exception as e:
        print("error on boost_id %s" % boost_id)
        raise e


if __name__ == "__main__":
    with app.app_context():
        main()
