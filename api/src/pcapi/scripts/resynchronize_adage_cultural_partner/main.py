import datetime

import pcapi.core.educational.api.adage as adage_api
from pcapi.models import db


if __name__ == "__main__":
    from pcapi.flask_app import app

    app.app_context().push()

    timestamp = datetime.datetime(2024, 10, 7).timestamp()
    adage_api.synchronize_adage_ids_on_venues(debug=True, timestamp=timestamp)
    db.session.commit()
