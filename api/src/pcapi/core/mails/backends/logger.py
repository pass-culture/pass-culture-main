from dataclasses import asdict
import json
import logging
import smtplib
import typing

from .. import models
from .base import BaseBackend


logger = logging.getLogger(__name__)


class LoggerBackend(BaseBackend):
    """A backend that logs e-mail instead of sending it.
    It should be used for local development, and on testing/staging
    when performing load tests when we don't want to overload Sendinblue.
    """

    def send_mail(
        self,
        recipients: typing.Iterable[str],
        data: models.TransactionalEmailData | models.TransactionalWithoutTemplateEmailData,
        bcc_recipients: typing.Iterable[str] = None,
    ) -> models.MailResult:
        recipients = ", ".join(recipients)
        if bcc_recipients:
            bcc_recipients = ", ".join(bcc_recipients)
        sent_data = asdict(data)
        logger.info("An e-mail would be sent via Sendinblue to=%s, bcc=%s: %s", recipients, bcc_recipients, sent_data)
        result = models.MailResult(sent_data=sent_data, successful=True)

        try:
            json_object = json.dumps(sent_data["params"], indent=4)
            from_addr = f"{sent_data['reply_to']['name']} <{sent_data['reply_to']['email']}>"
            template_id_str = str(sent_data["template"]["id_not_prod"])
            logger.info("will format")
            message = """From: %s
To: %s
MIME-Version: 1.0
Content-type: text/plain
Subject: e-mail test #%s

%s
""" % (
                from_addr,
                recipients,
                template_id_str,
                json_object,
            )
            logger.info("will send")
            smtp_obj = smtplib.SMTP()
            smtp_obj.connect("localhost", 1025)
            smtp_obj.sendmail(from_addr, recipients, message)
            logger.info("Successfully sent email")
        except Exception as exc:
            log = "If you need to receive those email: docker run -p 1080:1080 -p 1025:1025 maildev/maildev (%s)" % exc
            logger.info(log)

        return result
