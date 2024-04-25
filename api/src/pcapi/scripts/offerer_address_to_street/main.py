import math

from sqlalchemy import func

from pcapi.core.offerers.models import Offerer
from pcapi.flask_app import app
from pcapi.models import db


def copy_address_to_street_offerer() -> None:
    batch_size = 1000

    max_id = db.session.query(func.max(Offerer.id)).scalar()
    number_of_batch = math.ceil(max_id / batch_size)
    number_of_batch_done = 0
    ranges = [(i, i + batch_size) for i in range(0, max_id + 1, batch_size)]

    for start, end in ranges:
        db.session.execute(
            """
            UPDATE offerer
            SET street = address
            WHERE
            id BETWEEN :start AND :end
            AND address IS NOT NULL
            """,
            {"start": start, "end": end},
        )
        db.session.commit()
        number_of_batch_done += 1
        print("Street update ongoing... batch %s of %s" % (number_of_batch_done, number_of_batch))


if __name__ == "__main__":
    app.app_context().push()

    copy_address_to_street_offerer()
