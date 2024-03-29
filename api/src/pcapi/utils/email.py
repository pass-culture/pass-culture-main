import email_validator
import email_validator.syntax


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
