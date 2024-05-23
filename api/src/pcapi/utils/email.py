import logging

import email_validator
import email_validator.syntax

from pcapi import settings


logger = logging.getLogger(__name__)


def anonymize_email(email: str) -> str:
    try:
        name, domain = email.split("@")
    except ValueError:
        logger.exception("User email %s format is wrong", email)
        return "***"

    if len(name) > 3:
        hidden_name = name[:3]
    elif len(name) > 1:
        hidden_name = name[:1]
    else:
        hidden_name = ""

    return f"{hidden_name}***@{domain}"


def sanitize_email(email: str) -> str:
    return email.strip().lower()


def is_valid_email_or_email_domain(content: str) -> bool:
    return is_valid_email(content) or is_valid_email_domain(content)


def is_valid_email(content: str) -> bool:
    try:
        email_validator.validate_email(content, check_deliverability=False)
        return True
    except email_validator.EmailNotValidError:
        return False


def is_valid_email_domain(content: str) -> bool:
    if not content.startswith("@"):
        return False

    try:
        email_validator.syntax.validate_email_domain_name(content[1:])
        return True
    except email_validator.EmailNotValidError:
        return False


def is_email_whitelisted(email: str) -> bool:
    # Returns True if email domain is found in WHITELISTED_EMAIL_RECIPIENTS
    # To whitelist a domain, the format must be '*@my.domain';
    if not is_valid_email(email):
        return False
    domain = f"*@{email.split('@')[1]}"
    return email in settings.WHITELISTED_EMAIL_RECIPIENTS or domain in settings.WHITELISTED_EMAIL_RECIPIENTS
