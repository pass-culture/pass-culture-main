# Package `emails`

- [Dashboard Mailjet](https://app.mailjet.com/Dashboard) ;
- [Documentation Mailjet V3](https://dev.mailjet.com/email/guides/send-api-V3/).

## Dictionnaire à retourner

```python
{
    'FromEmail': SUPPORT_EMAIL_ADDRESS,
    'MJ-TemplateID': [XXX],
    'MJ-TemplateLanguage': True,
    'To': [email_du_destinataire],
    'Vars': {
        'booking_date': formatted_booking_date,
        'env': environment,
        'is_free_offer': is_free_offer,
        'offer_id': offer_id,
        'offer_price': stock_price,
        'venue_name': venue_name,
        '...': ...,
    }
}
```

Dans `Vars`, on peut y mettre :

- Des chaînes de caractères comme le nom de l'offre... ;
- Des booléens commençant par `is_` sous forme d'entier ;
- Des dates sous forme de chaîne de caractères ;
- Des prix sous forme de chaîne de caractères ;
- Des id humanisé sous forme de chaîne de caractères.

## Fonctions utiles

- `feature_send_mail_to_users_enabled()` ;
- `format_environment_for_email()` ;
- `get_date_formatted_for_email()` ;
- `get_time_formatted_for_email()` ;
- `humanize()` ;
- `utc_datetime_to_department_timezone()`.

## Constantes utiles

- `DEV_EMAIL_ADDRESS` ;
- `SUPPORT_EMAIL_ADDRESS`.

## Pour tester l'envoi d'un e-mail

- `pc python` ;
- Coller un des exemples ci-dessous ;
- Vérifier dans son client e-mail sa réception ;
- S'il n'a pas été reçu, regarder en bas du dashboard de Mailjet pour plus ample information.

```python
from pcapi.utils.mailing import send_raw_email
from pcapi.repository.user_queries import find_user_by_email
from pcapi.domain.user_emails import send_activation_email

user = find_user_by_email('prenom.nom+test@passculture.app')
with app.app_context():
    send_activation_email(user, send_raw_email)
```

```python
from pcapi.utils.mailing import send_raw_email
from pcapi.repository.booking_queries import find_by
from pcapi.domain.user_emails import send_booking_recap_emails

booking = find_by(token='VU6MMM')
with app.app_context():
    send_booking_recap_emails(booking, send_raw_email)
```

```python
from pcapi.utils.mailing import send_raw_email
from pcapi.repository.booking_queries import find_by
from pcapi.domain.user_emails import send_beneficiary_booking_cancellation_email

booking = find_by(token='100002')
with app.app_context():
    send_beneficiary_booking_cancellation_email(booking, send_raw_email)
```

```python
from pcapi.utils.mailing import send_raw_email
from pcapi.repository.booking_queries import find_by
from pcapi.domain.user_emails import send_booking_confirmation_email_to_beneficiary

booking = find_by(token='100002')
with app.app_context():
    send_booking_confirmation_email_to_beneficiary(booking, send_raw_email)
```

```python
from pcapi.utils.mailing import send_raw_email
from pcapi.repository.booking_queries import find_by
from pcapi.domain.user_emails import send_warning_to_beneficiary_after_pro_booking_cancellation

booking = find_by(token='100002')
with app.app_context():
    send_warning_to_beneficiary_after_pro_booking_cancellation(booking, send_raw_email)
```
