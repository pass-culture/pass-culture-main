---
sidebar_position: 2
description: How to authenticate messages coming from the pass Culture application
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Authenticating our messages

In the provider account creation process, you have been given **an API key**, to authenticate your call to our API, along with **a HMAC key**. You can either use the hmac key or our public key to authenticate our messages.

## HMAC

The symetrical HMAC authentication method should be considered deprecated and not be used for new implementations.

### What happens on our side

When we are about to send you a message, **we compute the signature of our request payload (i.e. our request body) using the HMAC key**.
The algorithm used is **sha256**.

Here is how we compute the signature:
```python
import hmac
from hashlib import sha256

def generate_signature(json_string: str):
    return hmac.new(YOUR_HMAC_KEY.encode(), json_string.encode(), sha256).hexdigest()
```

**The computed signature is then added to our request headers, in the *`PassCulture-Signature` header***.

### What should be checked on your side

When you receive a request on one of your messaging URLs, you can check that the message is coming from the pass Culture servers by following this **two steps process** :

1. Check that **the request has a `PassCulture-ed25519-Signature` header**
2. Check that **the signature of the request body is equal to the signature given in the `PassCulture-Signature` header**

Here are some implementation examples:

<Tabs>
<TabItem value="python" label="Python (Flask)">

```py
from flask import request, jsonify
import hmac
from hashlib import sha256

PASSCULTURE_HMAC_KEY = YOUR_HMAC_KEY  # should come from an env variable

app = Flask(__name__)

def _verify_signature(data: str, signature: str):
    # check that the signature of the body is matching the signature sent in the header
    return hmac.new(PASSCULTURE_HMAC_KEY.encode(), data.encode(), sha256).hexdigest() ==  signature

# the URL controller
@app.post('/tickets/create')
def create_ticket():
    request_signature = request.headers.get('PassCulture-Signature')

    if not request_signature:
        # `PassCulture-Signature` header is missing
        return jsonify({"message": "Invalid Signature"}), 401

    if not _verify_signature(request.json, request.headers.get('PassCulture-Signature')):
        # the request body signature doesn't match the signature in the `PassCulture-Signature` header
        return jsonify({"message": "Invalid Signature"}), 401

    # ... (your business logic)

    return jsonify(response_object), 200


if __name__ == '__main__':
    app.run()
```

</TabItem>
<TabItem value="js" label="Javascript (express)">

```js
const express = require('express');
const app = express();
const crypto = require('crypto');

app.use(express.json());

const PASSCULTURE_HMAC_KEY = 'YOUR_HMAC_KEY';  // should be stored in an env variable

// Function checking that the signature is matching
const verifySignature = (jsonString, signature) => {
    const hmac = crypto.createHmac('sha256', PASSCULTURE_HMAC_KEY);
    hmac.update(jsonString);
    return signature === hmac.digest('hex');
};

// the URL controller
app.post('/tickets/create', (req, res) => {
    // Access the JSON body from req.body
    const jsonString = JSON.stringify(req.body);
    const signature = req.get('PassCulture-Signature');

    if (!signature) {
        // `PassCulture-Signature` header is missing
        return res.status(401).json({
            message: 'Invalid Signature'
        });
    }

    if (!verifySignature(jsonString, signature)) {
        // the request body signature doesn't match the signature in the `PassCulture-Signature` header
        return res.status(401).json({
            message: 'Invalid Signature'
        });
    }

    // ... (your business logic)

    // Send a response
    res.status(200).json({
        message: 'Data received',
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
```

</TabItem>
<TabItem value="php" label="PHP (Symfony)">

```php
<?php

namespace App\Controller;

use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\StreamFactoryInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\HttpClient\Psr18Client;
use Symfony\Component\HttpClient\ScopingHttpClient;

class TicketController extends AbstractController
{
    private const PASSCULTURE_HMAC_KEY = 'YOUR_HMAC_KEY';  // should be stored in an env variable

    /**
     * @Route("/tickets/create", name="create_ticket", methods={"POST"})
     */
    public function createTicket(Request $request): Response
    {
        $jsonString = $request->getContent();
        $signature = $request->headers->get('PassCulture-Signature');

        if (!$signature) {
            return $this->json([
                'message' => 'Invalid Signature'
            ], 401);
        }

        if (!$this->verifySignature($jsonString, $signature)) {
            return $this->json([
                'message' => 'Invalid Signature'
            ], 401);
        }

        // Your business logic goes here...

        // Send a response
        return $this->json([
            'message' => 'Data received'
        ]);
    }

    private function verifySignature(string $jsonString, string $signature): bool
    {
        $hmac = hash_hmac('sha256', $jsonString, self::PASSCULTURE_HMAC_KEY);
        return hash_equals($signature, $hmac);
    }
}

```

</TabItem>
</Tabs>

## Asymetrical signature

This is the current authentication method. It does not rely on a shared secret anymore. New implementations should use this.

### What happens on our side

When we are about to send you a message, **we compute the signature of our request payload (i.e. our request body) using our private cryptographic key**.
The algorithm used is **ed25519**.

Here is how we compute the signature:
```python
from cryptography.hazmat.primitives import serialization

def generate_ed25519_signature(json_string: str) -> str:
    private_key = serialization.load_pem_private_key(PRIVATE_KEY.encode("utf-8"))
    return private_key.sign(json_string.encode("utf-8")).hex()
```

**The computed signature is then added to our request headers, in the *`PassCulture-ed25519-Signature` header***.

### What should be checked on your side

When you receive a request on one of your messaging URLs, you can check that the message is coming from the pass Culture servers by following this **two steps process** :

1. Check that **the request has a `PassCulture-ed25519-Signature` header**
2. Verify **the signature of the request body with the `PassCulture-ed25519-Signature` header**

Here are some implementation examples:

<Tabs>
<TabItem value="python" label="Python (Flask)">

```py
from flask import request, jsonify
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization


app = Flask(__name__)

def _verify_signature(data: str, signature: str) -> str:
    # check that the signature of the body is matching the signature sent in the header
    public_key = serialization.load_pem_public_key(PASS_CULTURE_PEM_PUBLIC KEY.encode('utf-8')) # uses the PEM version
    try:
        public_key.verify(
            signature=bytes.fromhex(signature),
            data=data.encode('utf-8'),
        )
    except InvalidSignature:
        return False
    return True

# the URL controller
@app.post('/tickets/create')
def create_ticket():
    request_signature = request.headers.get('PassCulture-ed25519-ignature')

    if not request_signature:
        # `PassCulture-Signature` header is missing
        return jsonify({"message": "Invalid Signature"}), 401

    if not _verify_signature(request.json, request.headers.get('PassCulture-ed25519-Signature')):
        # the request body signature doesn't match the signature in the `PassCulture-ed25519-Signature` header
        return jsonify({"message": "Invalid Signature"}), 401

    # ... (your business logic)

    return jsonify(response_object), 200


if __name__ == '__main__':
    app.run()
```

</TabItem>
<TabItem value="js" label="Javascript (express)">

```js
const express = require('express');
const app = express();
const crypto = require('crypto');

app.use(express.json());

const PASSCULTURE_PUBLIC_KEY = `-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAs1POvAYN7H3Cc6L5jKA1FXlt+lblpktDrKFkk+xUD1c=
-----END PUBLIC KEY-----`;  // should be stored in an env variable

// Function checking that the signature is matching
const verifySignature = (jsonString, signature) => {
    return crypto.verify(
      null,  // mandatory for Ed25519
      Buffer.from(jsonString, 'utf8'),
      Buffer.from(PASSCULTURE_PUBLIC_KEY, 'utf-8'),
      Buffer.from(signature, 'hex')
    );
};

// the URL controller
app.post('/tickets/create', (req, res) => {
    // Access the JSON body from req.body
    const jsonString = JSON.stringify(req.body);
    const signature = req.get('PassCulture-ed25519-Signature');

    if (!signature) {
        // `PassCulture-ed25519-Signature` header is missing
        return res.status(401).json({
            message: 'Invalid Signature'
        });
    }

    if (!verifySignature(jsonString, signature)) {
        // the request body signature doesn't match the signature in the `PassCulture-ed25519-Signature` header
        return res.status(401).json({
            message: 'Invalid Signature'
        });
    }

    // ... (your business logic)

    // Send a response
    res.status(200).json({
        message: 'Data received',
    });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
```

</TabItem>
<TabItem value="php" label="PHP (Symfony)">

```php
<?php

namespace App\Controller;

use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;
use Psr\Http\Message\StreamFactoryInterface;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;
use Symfony\Component\HttpClient\Psr18Client;
use Symfony\Component\HttpClient\ScopingHttpClient;

class TicketController extends AbstractController
{
    private const PASSCULTURE_PUBLIC_KEY = "-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAs1POvAYN7H3Cc6L5jKA1FXlt+lblpktDrKFkk+xUD1c=
-----END PUBLIC KEY-----";  // should be stored in an env variable

    /**
     * @Route("/tickets/create", name="create_ticket", methods={"POST"})
     */
    public function createTicket(Request $request): Response
    {
        $jsonString = $request->getContent();
        $signature = $request->headers->get('PassCulture-ed25519-Signature');

        if (!$signature) {
            return $this->json([
                'message' => 'Invalid Signature'
            ], 401);
        }

        if (!$this->verifySignature($jsonString, $signature)) {
            return $this->json([
                'message' => 'Invalid Signature'
            ], 401);
        }

        // Your business logic goes here...

        // Send a response
        return $this->json([
            'message' => 'Data received'
        ]);
    }

    private function verifySignature(string $jsonString, string $signature): bool
    {
        $bin_signature = hex2bin($signature);
        $public_key = openssl_pkey_get_public(self::PASSCULTURE_PUBLIC_KEY);
        $ok = openssl_verify(
            $jsonString,
            $bin_signature,
            $public_key,
            0 // no hash algorithm to provide as ed25519 provides its own
        )
        return ($ok === 1);
    }
}
?>
```
</TabItem>
</Tabs>

### Public keys

The public keys to use for the environments. These keys are PEM encoded:

<Tabs>
<TabItem value="prod" label="Production">
```
// TODO
```
</TabItem>
<TabItem value="integration" label="Integration">
```
-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAs1POvAYN7H3Cc6L5jKA1FXlt+lblpktDrKFkk+xUD1c=
-----END PUBLIC KEY-----
```
</TabItem>
</Tabs>