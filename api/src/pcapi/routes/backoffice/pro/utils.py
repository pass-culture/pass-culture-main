from dataclasses import dataclass
from random import randint

from flask_wtf import FlaskForm

from pcapi import settings
from pcapi.core.permissions import models as perm_models
from pcapi.routes.backoffice import utils

from . import forms


CONNECT_AS_OBJECT_TYPES = frozenset(
    (
        "bank_account",
        "collective_offer",
        "collective_offer_template",
        "offer",
        "offerer",
        "user",
        "venue",
    ),
)


@dataclass
class ConnectAs:
    form: FlaskForm
    formName: str
    href: str


def get_connect_as(object_type: str, object_id: int, pc_pro_path: str) -> ConnectAs | None:
    if object_type not in CONNECT_AS_OBJECT_TYPES:
        raise ValueError("Only types defined in CONNECT_AS_OBJECT_TYPES are accepted")

    if not pc_pro_path.startswith("/"):
        raise ValueError('pc_pro_path must be an absolute path in pc_pro (starting with "/")')

    if not utils.has_current_user_permission(perm_models.Permissions.CONNECT_AS_PRO):
        return None

    pc_pro_url = f"{settings.PRO_URL}{pc_pro_path}"
    random_int = randint(100000, 999999)
    form_name = f"connect-as-form-{object_type}-{object_id}-{random_int}"
    form = forms.ConnectAsForm(
        object_type=object_type,
        object_id=object_id,
        redirect=pc_pro_path,
    )
    return ConnectAs(
        form=form,
        formName=form_name,
        href=pc_pro_url,
    )
