---
sidebar_position: 2
---

# Create a collective offer

## Phase 1: Set-up your accounts

### Step 1: Get your provider account in the test environment

To be able to develop an integration to the pass Culture application, you need to have **a provider account in the integration test environment**. The process to request your provider account can be found [**here**](/docs/mandatory-steps/request-a-provider-account#how-to-get-a-provider-account).

Once our support team has created your provider account, they will send you an email with:

- an **API key** to authenticate your calls to our REST API
- an **HMAC key** to authenticate our requests to your application

:::danger
The **API key** and the **HMAC key** are sensitive pieces of information, so **you should store them in a safe place** and **_never_ commit them in plain text**.
:::

### Step 2: Create a pro account and a venue

If you have not already created a pro account in the integration test environment, create one following [**this process**](/docs/mandatory-steps/create-test-accounts).

Then log with this account [**on the pro interface in the integration test environment**](https://integration.passculture.pro/connexion). 

**Create a venue**

### Step 3: Link a venue to your provider

To be able to create a collective offer for a venue, you need to give access to this venue to your provider.

Go to the venue settings page (the URL of this settings page has the following pattern `https://pro.intergration.passculture.pro/structures/{offerer_id}/lieux/{venue_id}/parametres`), and add your provider in `Gestion des synchronisations` section using the `Selectionner un logiciel` button. You provider has now access to the venue.

## Phase 2: Build your integration

To build your integration you will be using the [**Create collective offer endpoint**](/rest-api#tag/Collective-Offers/operation/PostCollectiveOfferPublic).

Data necessary to the creation of a collective offer can be found in this section : [**Collective offer attributes**](/rest-api#tag/Collective-Offer-Attributes).

## Phase 3: Deploy your integration in production

If your integration is working properly in the integration test environment, you can [**contact our support team**](mailto:partenaires.techniques@passculture.app) to **request your provider account in production**.

They will send you an email with **your API Key** for the **production environment**.

Deploy your code in production using thos new key and it's done : **your software can now create collective on the pass Culture app!**

:::warning
Note that in the integration test environment, all venues are linked to an Adage ID, which means you can create a collective offer for each of them. This is meant for simplifying the test of the collective offer creation functionality.

However, in the production environment, it won’t be the case : **a venue is not automatically referenced in the Adage ecosystem**. Please ensure that the venues for which you are planning to create collective offers are linked to an Adage ID ; otherwise, you will not be able to create collective offer for the venue
:::