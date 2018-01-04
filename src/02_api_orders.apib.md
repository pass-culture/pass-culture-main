### Orders [/orders]

An order is a confirmation of a transaction made with the pass culture:
    - acceptedOffer is the product
    - confirmationNumber is the token that confirms the transaction
    - orderStatus says if the order is done or waiting
    - seller is the organization or the localBusinness selling the product.

#### List All Orders [GET]

+ Response 200 (application/json)

        [
            {
                "acceptedOffer": {
                    "authors": [
                        {
                            "id" : "58c2b1d7920ea806e862234e",
                            "name": "Albert Camus"
                        }
                    ],
                    "id" : "58c2b1d7920ea806e862230a",
                    "title": "La Chute",
                    "type": "book",
                    "published_at": "2015-08-05T09:40:51.620Z"
                },
                "confirmationNumber": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
                "orderStatus": "done",
                "published_at": "2015-08-05T10:40:51.620Z",
                "seller":  {
                    "id" : "58c2b1d7920ea806e862230c",
                    "location": {
                            "address": "155 Rue Saint Honoré, 75001 Paris",
                            "geo": {
                                "latitude": 48.8619639,
                                "longitude": 2.3359426
                            }

                        },
                    "name": "Librairie Delamain",
                    "openingHours": "10AM-8PM"
                }
            }
        ]

#### Create New Order [POST]

When you are using the CLIENT part of the app, you may create your own order using this action.
    - customerId is the id of the client

+ Request (application/json)

        {
            "acceptedOfferId": "58c2b1d7920ea806e862230e",
            "customerId": "58c2b1d7920ea806e862335a",
            "sellerId": "58c2b1d7920ea806e862335b"
        }

+ Response 201 (application/json)

    + Headers

            Location: /orders/2

    + Body

            {
                "confirmationNumber": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
                "orderStatus": "waiting",
                "id" : "58c2b1d7920ea806e862231a",
                "published_at": "2015-08-05T10:40:51.620Z"
            }
