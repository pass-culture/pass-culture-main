curl -X POST http://localhost:5001/public/offers/v1/products/ean \
-H "Content-Type: application/json" \
-H "Authorization: Bearer 398891255_testing_Test" \
-d '{
  "location": {
    "type": "physical",
    "venueId": 820 
  },
  "products": [
    {
      "ean": "6953051325254",
      "stock": {
        "price": 1234,
        "quantity": 103
      }
    }
  ]
}' \
-w "\nStatus: %{http_code}\n"
