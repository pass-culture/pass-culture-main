---
sidebar_position: 3
---

# Create a collective offer

## Setup

First, set up your provider if you haven't already done so (more information [**here**](/docs/mandatory-steps/request-a-provider-account#how-to-get-a-provider-account).

Next step is to ensure that your API key is linked to at least one venue.

:::warning
Note that in an integration environment, all venues are linked to an Adage ID, which mean you are allowed to created a collective offer, in order to test it. However, in the production environment it won’t be the case : a venue is not automatically referenced Adage. Please ensure that your linked venues can be used for collective offers.
:::

## API: create a bookable offer

Here's an example.

`POST /v2/collective/offers/`

Your JSON payload should look something like :
```json
{
  "venueId": 1234,
  "name": "Atelier de peinture",
  "description": "Describe your offer",
  "subcategoryId": "ATELIER_PRATIQUE_ART",
  "formats": [
    "Atelier de pratique"
  ],
  "bookingEmails": [
    "notifications.update@email.com"
  ],
  "contactEmail": "somebody.to.contact@gmail.com",
  "contactPhone": "0908070605",
  "domains": [
    1,
    2
  ],
  "students": [
    "GENERAL2",
    "GENERAL1",
    "GENERAL0"
  ],
  "audioDisabilityCompliant": true,
  "visualDisabilityCompliant": true
  "mentalDisabilityCompliant": true,
  "motorDisabilityCompliant": true,
  "offerVenue": {
    "addressType": "offererVenue",
    "otherAddress": null,
    "venueId": 1234
  },
  "isActive": true,
  "beginningDatetime": "2024-07-25T14:00:00+02:00",
  "startDatetime": "2024-07-25T14:00:00+02:00",
  "endDatetime": "2024-07-25T19:00:00+02:00",
  "bookingLimitDatetime": "2024-07-25T14:00:00+02:00",
  "totalPrice": 100,
  "numberOfTickets": 10,
  "educationalInstitution": "0010008D",
  "nationalProgramId": 2,
  "durationMinutes": 60,
  "imageFile": "",
  "imageCredit": "",
  "educationalPriceDetail": "10 tickets x 10 € = 100 €"
}
```

| Key              | Type | Nullable | Explanation |
| :---------------- | :------ | :----: | :-------- |
| **venueId** | Integer | **`false`** | Your administrative venue that handles the offer. Note that it can also be the event location (see `offerVenue`) |
| **name** | String | **`false`** | Bookable offer name |
| **description** | String | **`false`** | Describe your offer, the educational purpose. Do not add any pricing detail here, see `educationalPriceDetail` |
| **subcategoryId** | String | `true` | Deprecated. Use `formats` but keep in mind that at least one must be set |
| **bookingEmails** | List[String] | **`false`** | Booking notification email addresses |
| **contactEmail** | String | **`false`** | Contact email shown to the teacher/educational staff |
| **contactPhone** | String | **`false`** |  Contact phone shown to the teacher/educational staff |
| **domains** | List[Integer] | **`false`** | List of educational domain (ids) |
| **students** | List[String] | **`false`** | List of target student levels |
| **audioDisabilityCompliant** | Boolean | **`false`** | |
| **visualDisabilityCompliant** | Boolean | **`false`** | |
| **mentalDisabilityCompliant** | Boolean | **`false`** | |
| **motorDisabilityCompliant** | Boolean | **`false`** | |
| **offerVenue** | Object | **`false`** | Event location. All three keys are mandatory: `addressType`, `otherAddress`, `venueId` |
| **isActive** | Boolean | **`false`** | Mandatory but... deprecated. A collective offer will always be active |
| **beginningDatetime** | Stringified datetime (format **`YYYY-MM-DDTHH:mm:ss`**) | false | Deprecated. Start using `startDatetime` |
| **startDatetime** | Stringified datetime (format **`YYYY-MM-DDTHH:mm:ss`**) | `true` | |
| **endDatetime** | Stringified datetime (format **`YYYY-MM-DDTHH:mm:ss`**) | `true` | |
| **bookingLimitDatetime** | Stringified datetime (format **`YYYY-MM-DDTHH:mm:ss`**) | `true` | Set a booking date limit |
| **totalPrice** | Integer | **`false`** | |
| **numberOfTickets** | Integer | **`false`** | |
| **educationalPriceDetail** | String | `true` | Help the teacher/educational staff how tickets are handled: one for the whole group, one per student...|
| **educationalInstitution** | Integer | `true` | Adage's UAI("Unité Administrative Immatriculée"). One of `educationalInstitution`/`educationalInstitutionId` must be set |
| **educationalInstitutionId** | String | `true` | Our database id. One of `educationalInstitution`/`educationalInstitutionId` must be set |
| **nationalProgramId** | Integer | `true` | Set a national program. This is something quite specific, most offer might not be linked to any |
| **durationMinutes** | Integer | `true` | How long does it last? |
| **imageFile** | String | `true` | base64-encodede image. If set, `imageCredit` becomes mandatory|
| **imageCredit** | String | `true` | Image author/owner. If set, `imageFile` becomes mandatory|

### subcategoryId and formats
List of known subcategories can be found using the this route:
GET `/public/offers/v1/events/categories`

List of known formats can be found using this route:
GET `/v2/collective/offers/formats`

### domains
List of available educational domains can be found at:
GET `/v2/collective/educational-domains`

### students (mandatory)
List of available educational domains can be found at:
GET `/v2/collective/student-levels`

### offerVenue (mandatory)
Please refer to [the main bookable offer documentation for more details](/docs/understanding-our-api/resources/collective-offers).

### nationalProgramId (optional)
List of available national program ids can be found at:
GET `/v2/collective/national-programs/`
