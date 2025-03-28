---
sidebar_position: 1
description: How authentication and authorization work
---

# Authentication & Authorization

## Users

### Non technical users: beneficiaries and offerers

There are two main users of the pass Culture application :

#### Individual part

* **Beneficiary**, who are using their credit to buy cultural offers through the [web application](https://passculture.app/accueil) or the mobile application. A beneficiary is between 15 and 20 years and 11 months old.

:::note
For now, in the integration environment, your beneficiary account fakes an 18-year-old beneficiary with a € 300 credit.
:::

* **the cultural partners** who are providing those cultural offers through the **[pro interface](https://passculture.pro/) to the app**

#### Collective part

* The cultural partners who are providing those cultural offers through the **[pro interface](https://passculture.pro/) on the Adage plateform**
* There’s also the teaching staff, but they don’t book collective offer on the app, but on Adage interface. You can’t try this plateforme for now.

### Technical users: providers

As a technical partner, you belong to a third kind of user : the **providers**. Providers are **authenticated by an API key** and interact with the pass Culture through its **[REST API](/rest-api/)**.
To be able to manage an offer, the providers need to be given access by the offerer to the venue to which the offer is linked.

## Authentication

### Prerequisite : Getting your API keys

**All our endpoints require you to be authenticated**. Authentication is done thanks to an **API key**. To get your API key, please see the **[Request a provider account documentation](/docs/mandatory-steps/request-a-provider-account)**.

:::warning
You will be given **a pair of API keys** by our support team :
- one to authenticate your calls to the **[integration test environment](https://backend.integration.passculture.pro)**
- one to authenticate you calls to the **[production environment](https://backend.passculture.app)**

**⚠️ Make sure to use the right API key for the right environment.**
:::

### Authenticating your requests with your API key

Once you have your API key, add it in your request headers to authenticate your request. The API key should be located in the **Authorization header**, using the **`Bearer` pattern** (see example below).

```bash
# Example of an authenticated request using curl
# Fetch event categories on the integration test environment

curl --location 'https://backend.integration.passculture.team/public/offers/v1/events/categories' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer {you-api-key}'
```


## Authorization

Once you are authenticated as a **provider**, your goal is to be able to manage **`offers`** (products or events) and their **`bookings`** using our REST API.

To be able to perform those actions, **you need to be given access to the `venue` linked to those `offers`**.

### Understanding the key resources: `Offerers` and `Venues`

An **`offerer`** represents the **main company** in the French administrative system, identified by a **SIREN** (_Système d'Identification du Répertoire des Entreprises_).

A **`venue`** is an **entity responsible for managing offers**, such as a theater, concert hall, museum, bookshop, cinema, or concert producer. While it has a physical location, its primary purpose is to centralize a cultural partner's administrative information. In the French administrative system, it is identified by a **SIRET** (_Système d'Identification du Répertoire des Établissements_).

For instance, the pass Culture Office is a `venue` (SIRET: *853 318 459 00049*), owned by the `offerer` pass Culture (SIREN: *853 318 459*).

### Gaining access to a `venue`

The access to the venue will be given to you either :

- **_by the offerer_ in the [pro interface](https://passculture.pro/), if your are developing a _public_ integration**, that is to say an integration that can be used by several **`offerers`**.
  
  _For instance, if you are developing a ticketing software and your solution is used by several companies (theaters, museums, stadiums...) each of your client will need to give you access to their venues in the **[pro interface](https://passculture.pro/)**._
- **_by our support team_ if you are developing a _private_ integration**. This situation is relevant for internal technical teams that are developing an integration for their company that won't be used by other **`offerers`**.

:::tip
If you want **to know which venues are linked to your provider account**, you can use this **[endpoint](/rest-api/#tag/Venues/operation/GetOffererVenues)**. It is possible to filter by offerer, using the offerer's SIREN.

If you want **to know if a specific venue is linked to your provider account**, you can use the [**Get Venue endpoint**](/rest-api#tag/Venues/operation/GetVenueBySiret). 
If the venue exists in our database and your provider is linked to this venue, the endpoint will return the venue information; otherwise, it will return a **404 Not Found** error.


```bash
# Example requests with curl

# Return all the venues linked to your provider account
curl --location 'https://backend.integration.passculture.team/public/offers/v1/offerer_venues' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer {you-api-key}'

# Return all the venues linked to your provider account and belonging to the offerer whose siren is 123456789
curl --location 'https://backend.integration.passculture.team/public/offers/v1/offerer_venues?siren=123456789' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer {you-api-key}'

# Return a venue linked to your provider account and whose siret is 12345678900001
curl --location 'https://backend.integration.passculture.team/public/offers/v1/venues/12345678900001' \
--header 'Accept: application/json' \
--header 'Authorization: Bearer {you-api-key}'
```
:::

### Authorization errors

Usually the error code when an API user is trying to perform an action it is not allowed to perform is a **`HTTP 403`**. 

For security reasons, on the pass Culture API, **if you are trying to access or modify a resource you don't have access to, you will be returned a `HTTP 404` (i.e. resource not found)**.

You will be returne **`HTTP 403`** only in the case you are trying to perform a forbidden action on a resource you have access to (_for instance, trying to cancel an used booking_).
