from pcapi.routes.backoffice_v3.forms import fields
from pcapi.routes.backoffice_v3.forms import utils


class BlacklistDomainNameForm(utils.PCForm):
    domain = fields.PCDomainName("Nom de domaine")


class PrepareBlacklistDomainNameForm(BlacklistDomainNameForm):
    """
    Used to build and validate summary page, no data should be modified
    this form. To actually blacklist a domain name, use the form below.
    """

    class Meta:
        csrf = False
