import csv
import logging
import os

import pcapi.core.offerers.models as offerers_models
import pcapi.core.users.models as users_models
from pcapi.flask_app import app


logger = logging.getLogger(__name__)


EXCLUDED_OFFERERS_IDS = {
    7938,
    2061,
    3598,
    36110,
    5136,
    4112,
    3094,
    1558,
    40984,
    30237,
    33,
    3106,
    1059,
    20771,
    34596,
    38,
    38955,
    5165,
    1587,
    15923,
    5173,
    1337,
    22844,
    3397,
    4421,
    1610,
    26444,
    16719,
    849,
    37721,
    602,
    3164,
    865,
    41828,
    613,
    43364,
    358,
    3178,
    620,
    2676,
    4214,
    636,
    27275,
    29579,
    2955,
    1422,
    913,
    1426,
    403,
    27288,
    2975,
    675,
    420,
    43429,
    23208,
    5290,
    426,
    1966,
    4016,
    436,
    4025,
    4284,
    192,
    193,
    4290,
    195,
    22211,
    2244,
    25286,
    4038,
    4296,
    203,
    207,
    4047,
    723,
    5332,
    4054,
    217,
    730,
    3810,
    3044,
    229,
    998,
    239,
    499,
    248,
    6907,
    30463,
}

HEADERS = ["id", "email", "offererId"]


def extract_EPN_users() -> None:
    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/export_EPN_users.txt", "w", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(HEADERS)
        for user_infos in (
            users_models.User.query.join(offerers_models.UserOfferer, users_models.User.UserOfferers)
            .filter(
                offerers_models.UserOfferer.offererId.in_(EXCLUDED_OFFERERS_IDS),
            )
            .with_entities(users_models.User.id, users_models.User.email, offerers_models.UserOfferer.offererId)
            .all()
        ):
            writer.writerow(user_infos)


if __name__ == "__main__":
    app.app_context().push()
    extract_EPN_users()
