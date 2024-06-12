---
sidebar_position: 1
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Connect the pass Culture to your ticketing system

## Tutorial Goal

The goal of this tutorial is to explain step by step how to **set-up**, **build**, **test** and **deploy** an integration that connects the pass Culture application to your ticketing system.

Once your integration is up and running, you will receive ticket reservation/cancellation requests for the **events using your ticketing system**.

As it is a development tutorial, the pass Culture environment that will be used in the first three phases of this tutorial is the **integration test environment**.

## Phase 1: Set-up your accounts

### Step 1: Get your provider account in the test environment

To be able to develop an integration to the pass Culture application, you need to have **a provider account in the integration test environment**. The process to request your provider account can be found [**here**](/docs/mandatory-steps/request-a-provider-account#how-to-get-a-provider-account).

Once our support team has created your provider account, they will send you an email with:

- an **API key** to authenticate your calls to our REST API
- an **HMAC key** to authenticate our requests to your application

:::danger
The **API key** and the **HMAC key** are sensitive pieces of information, so **you should store them in a safe place** and **_never_ commit them in plain text**.
:::

### Step 2: Provide us with your notification URL and your cancellation URL

For the pass Culture to be connected with your ticketing system, **you need to have the booking URL and the cancellation URL set in your provider account**.

This set-up is currently done by our support team, so you should send as soon as possible your booking URL and your cancellation URL to [**our support team**](mailto:partenaires.techniques@passculture.app).

:::note
Keep in mind that, at this stage, you should send us your booking URL and your cancellation URL in your own test environment, as it is a development phase.
:::


## Phase 2: Build your integration

At this stage, you should create the two routes (the booking URL and the cancellation URL) and the business logic linked to those two routes. 

When building your integration, **you should pay attention** to two things:

- **the two URLs (booking & cancellation) must be freely accessible** (i.e. not protected by a your own authentication system), the authentication of the notification being done following [**this strategy**](/docs/understanding-our-api/notification-system/authenticating-our-notifications)
- **we expect specific response formats** : 
  - for ticket creation, we expect this [**success response**](/docs/understanding-our-api/managing-bookings/connection-with-ticketing-system#success-response) and those [**error responses**](/docs/understanding-our-api/managing-bookings/connection-with-ticketing-system#error-responses)
  - for ticket cancellation, we expect this [**success response**](/docs/understanding-our-api/managing-bookings/connection-with-ticketing-system#expected-response)

Here are some examples of what your integration could look like :

<Tabs>
<TabItem value="python" label="Python (Flask)">

```py
from flask import request, jsonify
import hmac
from hashlib import sha256

# should come from an env variable (as it is a very sensitive data & as it varies between envs)
PASSCULTURE_HMAC_KEY = os.getenv('YOUR_HMAC_KEY')
if not PASSCULTURE_HMAC_KEY:
    raise ValueError("HMAC key not found in environment variables")

app = Flask(__name__)


class PassCultureAuthenticationError(Exception):
    pass


# Service responsible for authenticating the pass Culture notifications
class PassCultureAuthenticationService:
    @staticmethod
    def _verify_signature(data: str, signature: str):
        # check that the signature of the body is matching the signature sent in the header
        return hmac.new(PASSCULTURE_HMAC_KEY.encode(), data.encode(), sha256).hexdigest() == signature

    @classmethod
    def authenticate_request(cls, request):
        request_signature = request.headers.get('PassCulture-Signature')
        
        if not request_signature or not cls._verify_signature(request.json, request.headers.get('PassCulture-Signature')):
            raise PassCultureAuthenticationError()


# Booking URL controller
@app.post('/your/booking/url')
def book_ticket():
    try:
        # checks that the request comes from the pass Culture
        PassCultureAuthenticationService.authenticate_request(request)

        # ... (your business logic)

        # Your success response
        return jsonify({
            "remainingQuantity": 12,  # the remaining quantity after this booking
            "tickets" : [{
                "barcode": "1234567AJSQ",  # the ticket barcode that will given to the beneficiary
                "seat": "A12"  # the ticket seat (if relevant)
            }],
        }), 200
    except PassCultureAuthenticationError: 
        # failed to authenticate the request
        return jsonify({"message": "Invalid Signature"}), 401
    except SoldOutError:  
        # error on your side because the event date is sold-out 
        return jsonify({
            "error": "sold_out",
            "remainingQuantity": 0
        }), 409
    except NotEnoughSeatsError:  
        # error on your side because we tried to book 2 seats and you have only one seat remaining
        return jsonify({
            "error": "not_enough_seats",
            "remainingQuantity": 1
        }), 409


# Cancellation URL controller
@app.post('/your/cancellation/url')
def cancel_ticket():
    try:
        # checks that the request comes from the pass Culture
        PassCultureAuthenticationService.authenticate_request(request)

        # ... (your business logic)

        # Your success response
        return jsonify({
            "remainingQuantity": 45,  # the remaining quantity after this cancellation
        }), 200
    except PassCultureAuthenticationError:
        # failed to authenticate the request
        return jsonify({"message": "Invalid Signature"}), 401


if __name__ == '__main__':
    app.run()
```

</TabItem>
<TabItem value="js" label="Javascript (express)">

```js
const express = require('express');
const crypto = require('crypto');
const bodyParser = require('body-parser');

// Initialize Express app
const app = express();
app.use(bodyParser.json());

// should come from an env variable (as it is a very sensitive data & as it varies between envs)
const PASSCULTURE_HMAC_KEY = process.env.YOUR_HMAC_KEY;
if (!PASSCULTURE_HMAC_KEY) {
    throw new Error("HMAC key not found in environment variables");
}

// Custom error classes
class PassCultureAuthenticationError extends Error {}

// Service responsible for authenticating the pass Culture notifications
class PassCultureAuthenticationService {
    static verifySignature(data, signature) {
        const hmac = crypto.createHmac('sha256', PASSCULTURE_HMAC_KEY);
        hmac.update(data);
        const expectedSignature = hmac.digest('hex');
        return crypto.timingSafeEqual(Buffer.from(expectedSignature), Buffer.from(signature));
    }

    static authenticateRequest(req) {
        const requestSignature = req.headers['passculture-signature'];
        if (!requestSignature || !this.verifySignature(JSON.stringify(req.body), requestSignature)) {   
            throw new PassCultureAuthenticationError("Invalid signature");
        }
    }
}

// Booking URL controller
app.post('/your/booking/url', (req, res) => {
    try {
        // Authenticate the request
        PassCultureAuthenticationService.authenticateRequest(req);

        // (Your business logic here)

        // Success response
        res.status(200).json({
            remainingQuantity: 12,  // the remaining quantity after this booking
            tickets: [{
                barcode: "1234567AJSQ",  // the ticket barcode given to the beneficiary
                seat: "A12"  // the ticket seat (if relevant)
            }],
        });
    } catch (error) {
        if (error instanceof PassCultureAuthenticationError) {
            // failed to authenticate the request
            res.status(401).json({ message: "Invalid signature" });
        } else if (error instanceof SoldOutError) {
            // error on your side because the event date is sold-out
            res.status(409).json({
                error: "sold_out",
                remainingQuantity: 0
            });
        } else if (error instanceof NotEnoughSeatsError) {
            // error on your side because we tried to book 2 seats and you have only one seat remaining
            res.status(409).json({
                error: "not_enough_seats",
                remainingQuantity: 1
            });
        } else {
            console.error(`Unhandled error: ${error.message}`);
            res.status(500).json({ message: "Internal server error" });
        }
    }
});

// Cancellation URL controller
app.post('/your/cancellation/url', (req, res) => {
    try {
        // Authenticate the request
        PassCultureAuthenticationService.authenticateRequest(req);

        // (Your business logic here)

        // Success response
        res.status(200).json({
            remainingQuantity: 45,  // the remaining quantity after this cancellation
        });
    } catch (error) {
        if (error instanceof PassCultureAuthenticationError) {
            // failed to authenticate the request
            res.status(401).json({ message: "Invalid signature" });
        } else {
            console.error(`Unhandled error: ${error.message}`);
            res.status(500).json({ message: "Internal server error" });
        }
    }
});

// Start the server
const port = process.env.PORT || 3000;
app.listen(port, () => {
    console.log(`Server is running on port ${port}`);
});

```

</TabItem>
<TabItem value="php" label="PHP (Symfony)">

```php
<?php

namespace App\Controller;

use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpKernel\Exception\HttpException;

class TicketController extends AbstractController
{
    private $passCultureHmacKey;

    public function __construct()
    {
        // should come from an env variable (as it is a very sensitive data & as it varies between envs)
        $this->passCultureHmacKey = $_ENV['YOUR_HMAC_KEY'];
        if (!$this->passCultureHmacKey) {
            throw new \Exception("HMAC key not found in environment variables");
        }
    }

    private function verifySignature($data, $signature)
    {
        $expectedSignature = hash_hmac('sha256', $data, $this->passCultureHmacKey);
        return hash_equals($expectedSignature, $signature);
    }

    private function authenticateRequest(Request $request)
    {
        $requestSignature = $request->headers->get('PassCulture-Signature');
        if (!$requestSignature || !$this->verifySignature($request->getContent(), $requestSignature)) {
            throw new HttpException(401, "Invalid signature");
        }
    }

    /**
     * @Route("/your/booking/url", methods={"POST"})
     */
    public function bookTicket(Request $request)
    {
        try {
            $this->authenticateRequest($request);

            // (Your business logic here)

            // Success response
            return new JsonResponse([
                'remainingQuantity' => 12, // the remaining quantity after this booking
                'tickets' => [
                    [
                        'barcode' => '1234567AJSQ',  // the ticket barcode given to the beneficiary
                        'seat' => 'A12', // the ticket seat (if relevant)
                    ],
                ],
            ], 200);
        } catch (HttpException $e) {
            // failed to authenticate the request
            return new JsonResponse(['message' => $e->getMessage()], $e->getStatusCode());
        } catch (SoldOutError $e) {
            // error on your side because the event date is sold-out
            return new JsonResponse([
                'error' => 'sold_out',
                'remainingQuantity' => 0,
            ], 409);
        } catch (NotEnoughSeatsError $e) {
            // error on your side because we tried to book 2 seats and you have only one seat remaining
            return new JsonResponse([
                'error' => 'not_enough_seats',
                'remainingQuantity' => 1,
            ], 409);
        } catch (\Exception $e) {
            return new JsonResponse(['message' => 'Internal server error'], 500);
        }
    }

    /**
     * @Route("/your/cancellation/url", methods={"POST"})
     */
    public function cancelTicket(Request $request)
    {
        try {
            $this->authenticateRequest($request);

            // (Your business logic here)

            return new JsonResponse([
                'remainingQuantity' => 45,
            ], 200);
        } catch (HttpException $e) {
            return new JsonResponse(['message' => $e->getMessage()], $e->getStatusCode());
        } catch (\Exception $e) {
            return new JsonResponse(['message' => 'Internal server error'], 500);
        }
    }
}
```

</TabItem>
</Tabs>

## Phase 3: Test your integration

### Step 1: Create a pro account and a venue

If you have not already created a pro account in the integration test environment, create one following [**this process**](/docs/mandatory-steps/create-test-accounts).

Then log with this account [**on the pro interface in the integration test environment**](https://integration.passculture.pro/connexion). 

**Create a venue** and **link the venue to your provider account**.

### Step 2: Create an event linked to your ticketing system

**Create an event** for the venue you created in the previous step.

For that, you need:
- **to create an event with `hasTicket` set to `true`** and **having at least one price category**, using [**this endpoint**](/rest-api#tag/Event-offer/operation/PostEventOffer)
- **to add stocks for this newly created event**, using [**this endpoint**](/rest-api#tag/Event-offer-dates/operation/PostEventDates)

### Step 3: Try to book/cancel a ticket as a beneficiary

:::tip
**In the integration test environment, your pro account is also a beneficiary account credited with € 300**. This way you can easily test your creation without having to create two accounts.
:::

[**Log on the beneficiary interface**](https://integration.passculture.app/connexion?from=profile) and try to book a ticket for the event you created. If your integration works properly, your booking URL should be called by the pass Culture and you should receive, [**in the beneficiary interface**](https://integration.passculture.app/), the ticket barcode returned by your system.

Then, as a beneficiary, try to cancel the ticket you booked. If your integration works properly, your cancellation URL should be called by the pass Culture and you see a success message [**in the beneficiary interface**](https://integration.passculture.app/).

## Phase 4: Deploy your integration in production

If your integration is working properly in the integration test environment, you can [**contact our support team**](mailto:partenaires.techniques@passculture.app) to **request your provider account in production**. When you contact them, don't forget to give them **the booking URL** and **the cancellation URL** in **your production environment**.

They will send you an email with **your API Key** and **your HMAC key** for the **production environment**. 

Deploy your code in production using those new keys and it's done : **the pass Culture is now connected to your ticketing system !**
