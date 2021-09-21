from flask import url_for
from flask_saml2.sp import ServiceProvider


class EduconnectServiceProvider(ServiceProvider):
    def get_logout_return_url(self) -> str:
        return url_for("index", _external=True)

    def get_default_login_return_url(self) -> str:
        return url_for("index", _external=True)
