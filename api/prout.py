from datetime import datetime
import os
import pprint

import googlemaps

from pcapi import settings
from pcapi.core.object_storage import store_public_object
from pcapi.core.offerers import models as offerers_models
from pcapi.utils.image_conversion import process_original_image


gmaps = googlemaps.Client(key=os.environ.get("MAPS_API_KEY"))


# https://developers.google.com/maps/documentation/places/web-service/search-find-place
# https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=APOTHEK, Rue Notre Dame, Bordeaux&inputtype=textquery&fields=photos%2Cname%2Cplace_id&key=KEY --> INPUT : TEXT(NAME, address)
# Geocoding an address
# "APOTHEK, Rue Notre Dame, Bordeaux"
def get_venues_withouth_photo(begin: int | None = None, end: int | None = None, limit: int | None = None):
    query = (
        offerers_models.Venue.query.join(offerers_models.Offerer)
        .filter(
            offerers_models.Venue.isPermanent.is_(True),
            offerers_models.Venue.bannerUrl == None,
            offerers_models.Venue.venueTypeCode != "Lieu administratif",
            offerers_models.Offerer.isActive == True,
        )
        .order_by(offerers_models.Venue.id)
        .with_entities(offerers_models.Venue.id, offerers_models.Venue.address, offerers_models.Venue.name)
    )
    if begin is not None:
        query = query.filter(begin <= offerers_models.Venue.id)
    if end is not None:
        query = query.filter(offerers_models.Venue.id < end)
    if limit is not None:
        query = query.limit(limit)
    return [{"id": venue[0], "address": venue[1], "name": venue[2]} for venue in query]


# def get_venues_withouth_photo_test():
#     return [
#         {"id": 53369, "address": "14 RUE JEAN JACQUES HENNER", "name": "MUSEE DE L IMPRESS SUR ETOFFES"},
#         {"id": 3566, "address": "Rue du Languedoc", "name": "La Garance - Scène nationale de Cavaillon"},
#         {"id": 37425, "address": "Rue Raoul Follereau", "name": "Médiathèque de Lescar"},
#         {"id": 12679, "address": "16 a Avenue du Général Patton", "name": "Médiathèque Maison d'Elsa"},
#         {"id": 27881, "address": "Place du Docteur Guyot", "name": "Cinémobile CHATEAUMEILLANT"},
#         {"id": 27888, "address": "1 Place du Marché", "name": "Cinémobile MONDOUBLEAU"},
#         {"id": 5594, "address": "13 Rue de la République", "name": "MO.CO."},
#         {"id": 38793, "address": "28bis Rue Saint-Just", "name": " Conservatoire municipal de musique et de danse"},
#         {"id": 32177, "address": "35 RUE PASTEUR", "name": "ASSOCIATION LES DECABLES"},
#         {"id": 13896, "address": "93 RUE DU GEYSER", "name": "MJC MONTROND-LES-BAINS"},
#     ]


def get_place(name, address):
    result = gmaps.find_place(input=name + address, input_type="textquery", fields=["photos", "name", "place_id"])
    if len(result["candidates"]):
        return result["candidates"][0]
    return None


def is_the_bon_owner(name: str, photo: dict) -> bool:
    for attr in photo["html_attributions"]:
        if name in attr:
            return True
    return False


def get_place_photos(place_id):
    result = gmaps.place(place_id=place_id, fields=["photo", "name", "place_id"])
    if "photos" not in result["result"].keys():
        return None
    return result["result"]["photos"]


def get_owner_photo(photos, owner_name):
    for photo in photos:
        if is_the_bon_owner(owner_name, photo):
            return photo
    return None


def save_photo(photo):
    photos_result = gmaps.places_photo(
        photo_reference=photo["photo_reference"],
        max_width=photo["width"],
    )
    with open("image.jpeg", "wb") as f:
        for chunk in photos_result:
            if chunk:
                f.write(chunk)


storage_folder = settings.THUMBS_FOLDER_NAME + "/google_places"


def save_photo_to_gcp(venue_id, photo, owner: bool = False):
    photos_result = gmaps.places_photo(
        photo_reference=photo["photo_reference"],
        max_width=photo["width"],
    )
    owner_prefix = "owner_" if owner else ""
    object_id = f"google_places_{owner_prefix}{venue_id}.jpeg"
    data = bytes()
    for chunk in photos_result:
        if chunk:
            data += chunk
    store_public_object(storage_folder, object_id, process_original_image(content=data, resize=False), "image/jpeg")


if __name__ == "__main__":
    venues_without_photos = get_venues_withouth_photo(limit=100)
    print("the number of venues is:", len(venues_without_photos))
    places = dict()
    for venue in venues_without_photos:
        place = get_place(venue["name"], venue["address"])
        if place:
            places[venue["id"]] = place
    print("the number of places found on maps is:", len(places))
    places_with_at_least_one_photo = dict(filter(lambda place: "photos" in place[1], places.items()))
    print("the number of places found with at least one photo:", len(places_with_at_least_one_photo))
    photos_list = dict()
    for place_id, place_info in places_with_at_least_one_photo.items():
        photos = get_place_photos(place_info["place_id"])
        if photos:
            photos_list[place_id] = photos
    owner_photos = dict()
    for id, photos in photos_list.items():
        owner_photo = get_owner_photo(photos, places[id]["name"])
        if owner_photo:
            owner_photos[id] = owner_photo
    print("the number of places found with owner photo:", len(owner_photos))
    for id in photos_list.keys():
        if id in owner_photos.keys():
            save_photo_to_gcp(id, owner_photos[id], True)
        else:
            save_photo_to_gcp(id, photos_list[id][0], False)


# {'candidates': [{'name': 'APOTHEK', 'photos': [{'height': 1960, 'html_attributions': ['<a href="https://maps.google.com/maps/contrib/115194867939208656152">Olivier Sempé</a>'], 'photo_reference': 'ATJ83zh2WFszrMem3ENQUlyD0gexYozGu_38Jz8hxvUtKcSbCEoNaxMbYQhRyPBNuwv7uGaogt5cHN00Do9GilXM2bvXcI-SpLqOHN9LAY8cJ4ZM7D-CMNXzjT_R2yxZUoasJfvELK4SyQU4zeHvN4-WWpUQMovp9SPTfQOaynou9WiylbX8', 'width': 4032}], 'place_id': 'ChIJkQykKD8pVQ0RCub_YF4pe9U'}], 'status': 'OK'}


# https://maps.googleapis.com/maps/api/place/photo?photo_reference=ATJ83zjFtdCAI5-yDRX3n8LFMyoGyfDFvrYm1gHMt3edPE3pALIdIeh5oh2CHi6PjupWS0ubTfhfbSg9V2KQrWxIlg2PbEXtX_1k4sqHZ9AlKd5-j-bnFPFyyW20tETjAg6qSF1LA9CXuccF9ZXzV3EAq2SQx9KXSD-gAb1mZimvdo8eIVhb&maxwidth=300&key=


# https://maps.googleapis.com/maps/api/place/details/json?place_id=ChIJkQykKD8pVQ0RCub_YF4pe9U&fields=name%2Cphotos&key=
