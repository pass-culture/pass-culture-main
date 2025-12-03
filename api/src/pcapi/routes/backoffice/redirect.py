import enum
import logging

from flask import redirect
from flask import render_template
from flask import request
from werkzeug.exceptions import BadRequest
from wtforms import validators

from pcapi.connectors import virustotal

from . import blueprint
from . import utils
from .forms import fields as forms_fields
from .forms import utils as forms_utils


logger = logging.getLogger(__name__)


class RedirectStopReason(enum.Enum):
    ERROR = "ERROR"
    MALICIOUS = "MALICIOUS"
    NOT_FOUND = "NOT_FOUND"
    PENDING = "PENDING"


class SafeRedirectForm(forms_utils.PCForm):
    class Meta:
        csrf = False

    url = forms_fields.PCStringField(validators=(validators.DataRequired(),))
    ignore = forms_fields.PCSelectField(
        choices=forms_utils.choices_from_enum(RedirectStopReason),
        validate_choice=True,
        validators=(validators.Optional(),),
    )


@blueprint.backoffice_web.route("/redirect", methods=["GET"])
@utils.custom_login_required(redirect_to=".home")
def safe_redirect() -> utils.BackofficeResponse:
    form = SafeRedirectForm(request.args)
    if not form.validate():
        raise BadRequest()

    url = form.url.data
    ignore = form.ignore.data

    try:
        virustotal.check_url_is_safe(url)
    except virustotal.NotFoundException:
        # Scan URL for next time
        virustotal.request_url_scan(url)

        if ignore == RedirectStopReason.NOT_FOUND.name:
            logger.info("Forced redirection", extra={"url": url, "ignore": ignore})
            return redirect(url, code=303)

        return render_template("home/redirect.html", url=url, reason=RedirectStopReason.NOT_FOUND.name)

    except virustotal.PendingAnalysisException:
        if ignore == RedirectStopReason.PENDING.name:
            logger.info("Forced redirection", extra={"url": url, "ignore": ignore})
            return redirect(url, code=303)
        return render_template("home/redirect.html", url=url, reason=RedirectStopReason.PENDING.name)

    except virustotal.MaliciousUrlException:
        if ignore == RedirectStopReason.MALICIOUS.name:
            logger.info("Forced redirection", extra={"url": url, "ignore": ignore})
            return redirect(url, code=303)
        return render_template(
            "home/redirect.html", url=url, url_id=virustotal.url_id(url), reason=RedirectStopReason.MALICIOUS.name
        )

    except virustotal.VirusTotalApiException:
        if ignore == RedirectStopReason.ERROR.name:
            logger.info("Forced redirection", extra={"url": url, "ignore": ignore})
            return redirect(url, code=303)
        return render_template("home/redirect.html", url=url, reason=RedirectStopReason.ERROR.name)

    return redirect(url, code=303)
