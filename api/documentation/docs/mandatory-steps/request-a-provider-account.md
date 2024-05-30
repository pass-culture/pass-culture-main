---
sidebar_position: 1
title: Request a provider account
description: How to get the necessary accesses to the pass Culture REST API
---

# Request a provider account

## Mandatory accesses to use our API

To be able to use our **[REST API](/rest-api/)**, you need two things:

1. to have a **provider account with its _API key_ (for authentication)**
2. to have **your provider account linked to the venues** for which you are supposed to manage offers, products and/or events **(for authorization)**

:::note
For more information on **how authentication and authorization work on our API**, please take a look at **[this documentation page](/docs/understanding-our-api/authentication-authorization)**.
:::

## How to get a provider account 

Getting your provider account in production is a **4 steps process**:

1. First, you need to **[fill this form](https://passculture.typeform.com/to/JHmbK9Hg)**.
2. Then, our support team **creates your provider account on our _integration test environment_** and **provides you with the API key** to authenticate yourself on this environment.
3. You develop your integration using this **integration test environment**. At this step you need to **[create test accounts](/docs/mandatory-steps/create-test-accounts)** to be able to test that your integration is properly working.
4. Once your integration is working properly on the integration test environment, our support team **creates your provider account on our production environment** and **gives you your production API key**. You will then be **ready to deploy your integration in production 🚀**.
