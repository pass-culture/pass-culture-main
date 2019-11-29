# Package `emails`

- [Dashboard Mailjet](https://app.mailjet.com/Dashboard).
- [Documentation Mailjet V3](https://dev.mailjet.com/email/guides/send-api-V3/).

## Pour tester l'envoie d'un e-mail via Mailjet

```python
from utils.mailing import send_raw_email
from repository.user_queries import find_user_by_email
from domain.user_emails import send_activation_email

user = find_user_by_email('fabien.mercier+test@passculture.app')
with app.app_context():
    send_activation_email(user, send_raw_email)
```

```python
from utils.mailing import send_raw_email
from repository.booking_queries import find_by
from domain.user_emails import send_booking_recap_emails

booking = find_by(token='VU6MMM')
with app.app_context():
    send_booking_recap_emails(booking, send_raw_email)
```
