# Offer creation

## create_offer: inputs

### Input parameters

#### create offer schema

```
name: str
subcategory_id: str
audio_disability_compliant: bool
mental_disability_compliant: bool
motor_disability_compliant: bool
visual_disability_compliant: bool

booking_contact: EmailStr | None = None
booking_email: EmailStr | None = None
description: str | None = None
duration_minutes: int | None = None
external_ticket_office_url: HttpUrl | None = None
ean: str | None
extra_data: typing.Any = None
id_at_provider: str | None = None
is_duo: bool | None = None
url: HttpUrl | None = None
withdrawal_delay: int | None = None
withdrawal_details: str | None = None
withdrawal_type: offers_models.WithdrawalTypeEnum | None = None
video_url: HttpUrl | None = None

is_national: bool | None = None
```

#### extra params

```
venue: offerers_models.Venue
offerer_address: offerers_models.OffererAddress | None = None
provider: providers_models.Provider | None = None
product: offers_models.Product | None = None
is_from_private_api: bool = False
venue_provider: providers_models.VenueProvider | None = None
```

### Steps

1. format extra data
2. [private api] check product and venue subcategory
3. [private api] check accessibility compliance
4. check withdrawal
5. check subcategory
6. check extra data
7. check is duo
8. check url - subcategory
9. check can input id at provider
10. check can input id at provider for this venue
11. check offer name does not contain EAN

### Which parameters are mandatory?

```
name: str
subcategory_id: str
audio_disability_compliant: bool
mental_disability_compliant: bool
motor_disability_compliant: bool
visual_disability_compliant: bool
venue: offerers_models.Venue
```

### General rules

1. An offer must have a `product` if its venue is a record store and its
subcategory a `SUPPORT_PHYSIQUE_MUSIQUE_CD`

### Fields rules

* `withdrawal_type`
    - cannot be set if `subcategory_id` does not allow it
    - implies `bookingContact`
    - no `withdrawal_delay` if no ticket
    - `withdrawal_delay` must be set if ticket (sent by email)
    - in app withdrawal only available for venues linked to a provider
* `subcategory_id`: must be known and selectable
* `extra_data`:
    - all mandatory fields must be set (`subcategory` dependent)
    - if EAN
        - must be a 13-characters string
        - must not exist (yet)
    - `MUSIC_TYPE` / `MUSIC_SUB_TYPE` / `SHOW_TYPE` / `SHOW_SUB_TYPE`
        - must be string or int or null
        - code must be known
        - code must be allowed
* `is_duo`: `subcategory_id` must allow `is_duo`
* `url`: can only be set if `subcategory_id` allows it / must be if needed.
* `id_at_provider`:
    - can only be set if provider exists
    - venue cannot already have another offer with the same id at provider
* `name`: cannot contain EAN

## Main categories

* things: physical goods (eg books, CDs...)
* digital things and show: podcast, e-book, audio streaming, recorded show...
* activity: festival, concert, online event...

### Warning

Digital shows does look like some activities... however, there subcategory's
definition have a significant difference: the latter are events (more on that
later) and the former not.
