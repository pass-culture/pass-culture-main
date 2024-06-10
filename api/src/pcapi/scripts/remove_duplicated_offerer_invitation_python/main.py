import logging

from pcapi.models import db


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        logger.info("Start delete duplicated offerer invitation")
        db.session.execute(
            """
                DELETE FROM offerer_invitation
                WHERE id=1748 and "offererId"=10820 and status='PENDING';
            """
        )
        db.session.commit()
        logger.info("Duplicated offerer invitation deleted")
