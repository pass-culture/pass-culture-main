---
sidebar_position: 2
description: How to authenticate notifications coming from the pass Culture application
---

# Authenticating our notifications

In the provider account creation process, you have been given **an API key**, to authenticate your call to our API, along with **a HMAC key**. 
**It is the HMAC key that should be used to authenticate our notifications.**

## What happens on our side

When we are about to send you a notification, **we compute the signature of our request payload (i.e. our request body) using the HMAC key**.
The algorithm used is **sha256**.

Here is how we compute the signature:
```python
import hmac
from hashlib import sha256

def generate_signature(json_string: str):
    return hmac.new(YOUR_HMAC_KEY.encode(), json_string.encode(), sha256).hexdigest()
```

**The computed signature is then added to our request headers, in the *`PassCulture-Signature` header***.

## What should be checked on your side

When you receive a request on one of the notification URLs you indicated to us, you can check that the notification is coming from the pass Culture servers by following this **two steps process** :

1. Check that **the request has a `PassCulture-Signature` header**
2. Check that **the signature of the request body is equal to the signature given in the `PassCulture-Signature` header**

Here is an example implementation on a flask server.

```python
from flask import request, jsonify
import hmac
from hashlib import sha256

PASSCULTURE_HMAC_KEY = YOUR_HMAC_KEY  # should come from an env variable

app = Flask(__name__)

def _verify_signature(data: str, signature: str):
    return hmac.new(PASSCULTURE_HMAC_KEY.encode(), data.encode(), sha256).hexdigest() ==  signature

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

