def test_public_api(client, app):
    response = client.get("/openapi.json")
    assert response.status_code == 200

    assert response.json["info"] == {
        "description": "This the documentation of the Pass Culture public REST API",
        "title": "Pass Culture REST API",
        "version": "1.0",
    }

    # Bookings Endppoints
    assert response.json["paths"]["/public/bookings/v1/bookings"] is not None
    assert response.json["paths"]["/public/bookings/v1/bookings"] is not None
    assert response.json["paths"]["/public/bookings/v1/bookings"] is not None
    assert response.json["paths"]["/public/bookings/v1/bookings"] is not None
    assert response.json["paths"]["/public/bookings/v1/bookings"] is not None
    assert response.json["paths"]["/public/bookings/v1/cancel/token/{token}"] is not None
    assert response.json["paths"]["/public/bookings/v1/keep/token/{token}"] is not None
    assert response.json["paths"]["/public/bookings/v1/token/{token}"] is not None
    assert response.json["paths"]["/public/bookings/v1/use/token/{token}"] is not None

    # Offers Endpoints
    assert response.json["paths"]["/public/offers/v1/events"] is not None
    assert response.json["paths"]["/public/offers/v1/events/categories"] is not None
    assert response.json["paths"]["/public/offers/v1/events/{event_id}"] is not None
    assert response.json["paths"]["/public/offers/v1/events/{event_id}/dates"] is not None
    assert response.json["paths"]["/public/offers/v1/events/{event_id}/dates/{date_id}"] is not None
    assert response.json["paths"]["/public/offers/v1/events/{event_id}/price_categories"] is not None
    assert (
        response.json["paths"]["/public/offers/v1/events/{event_id}/price_categories/{price_category_id}"] is not None
    )
    assert response.json["paths"]["/public/offers/v1/music_types"] is not None
    assert response.json["paths"]["/public/offers/v1/music_types/all"] is not None
    assert response.json["paths"]["/public/offers/v1/music_types/event"] is not None
    assert response.json["paths"]["/public/offers/v1/offerer_venues"] is not None
    assert response.json["paths"]["/public/offers/v1/products"] is not None
    assert response.json["paths"]["/public/offers/v1/products/categories"] is not None
    assert response.json["paths"]["/public/offers/v1/products/ean"] is not None
    assert response.json["paths"]["/public/offers/v1/products/{product_id}"] is not None
    assert response.json["paths"]["/public/offers/v1/show_types"] is not None
    assert response.json["paths"]["/public/offers/v1/{offer_id}/image"] is not None

    # Collective offers
    assert response.json["paths"]["/v2/collective/bookings/{booking_id}"] is not None
    assert response.json["paths"]["/v2/collective/categories"] is not None
    assert response.json["paths"]["/v2/collective/educational-domains"] is not None
    assert response.json["paths"]["/v2/collective/educational-institutions/"] is not None
    assert response.json["paths"]["/v2/collective/national-programs/"] is not None
    assert response.json["paths"]["/v2/collective/offerer_venues"] is not None
    assert response.json["paths"]["/v2/collective/offers/"] is not None
    assert response.json["paths"]["/v2/collective/offers/formats"] is not None
    assert response.json["paths"]["/v2/collective/offers/{offer_id}"] is not None
    assert response.json["paths"]["/v2/collective/student-levels"] is not None
    assert response.json["paths"]["/v2/collective/subcategories"] is not None
    assert response.json["paths"]["/v2/collective/venues"] is not None
