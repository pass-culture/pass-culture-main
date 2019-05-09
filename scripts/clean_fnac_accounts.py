from typing import List

from models import User, Offerer, PcObject, Offer, Venue
from models.db import db
from tests.test_utils import create_user_offerer


def find_all_fnac_users():
    is_fnac_email = User.email.endswith('@fnacdarty.com') | User.email.endswith('@fnac.com')
    return User.query.filter(is_fnac_email).all()


def find_all_OK_fnac_offerers():
    all_fnac_siren = ['350127460', '434001954', '334473352', '343282380']
    is_fnac_offerer = Offerer.siren.in_(all_fnac_siren)
    return Offerer.query.filter(is_fnac_offerer).all()


def create_all_possible_user_offerers(users: List[User], offerers: List[Offerer]):
    for user in users:
        for offerer in offerers:
            if offerer not in user.offerers:
                create_user_offerer(user, offerer)
    PcObject.check_and_save(*users)


def clear_all_existing_user_offerers(id: int):
    offerer = Offerer.query.filter_by(id=id).one()
    offerer.users = []
    PcObject.check_and_save(offerer)


def move_offers_from_one_venue_to_another(origin_venue_id: int, target_venue_id: int):
    offers = Offer.query.filter_by(venueId=origin_venue_id).all()
    offers = [_change_venue(offer, target_venue_id) for offer in offers]
    if offers:
        PcObject.check_and_save(*offers)


def delete_all_physical_managed_venues(offerer_id: int):
    fnac_live = Offerer.query.filter_by(id=offerer_id).one()
    for venue in fnac_live.managedVenues:
        if not venue.isVirtual:
            db.session.delete(venue)
    db.session.commit()


def clean_fnac_accounts():
    fnac_live_id = 181
    fnac_darty_participations_et_services_id = 437
    fnac_montpellier = {'id_ok': 3176, 'id_ko': 822}
    fnac_brest = {'id_ok': 3175, 'id_ko': 816}
    fnac_strasbourg = {'id_ok': 3168, 'id_ko': 815}
    fnac_parinor = {'id_ok': 3180, 'id_ko': 821}
    fnac_rosny = {'id_ok': 3179, 'id_ko': 820}
    fnac_quimper = {'id_ok': 3177, 'id_ko': 818}

    all_fnac_users = find_all_fnac_users()
    all_ok_fnac_offerers = find_all_OK_fnac_offerers()
    create_all_possible_user_offerers(all_fnac_users, all_ok_fnac_offerers)
    clear_all_existing_user_offerers(fnac_live_id)
    clear_all_existing_user_offerers(fnac_darty_participations_et_services_id)

    move_offers_from_one_venue_to_another(fnac_montpellier['id_ko'], fnac_montpellier['id_ok'])
    move_offers_from_one_venue_to_another(fnac_brest['id_ko'], fnac_brest['id_ok'])
    move_offers_from_one_venue_to_another(fnac_strasbourg['id_ko'], fnac_strasbourg['id_ok'])
    move_offers_from_one_venue_to_another(fnac_parinor['id_ko'], fnac_parinor['id_ok'])
    move_offers_from_one_venue_to_another(fnac_rosny['id_ko'], fnac_rosny['id_ok'])
    move_offers_from_one_venue_to_another(fnac_quimper['id_ko'], fnac_quimper['id_ok'])

    delete_all_physical_managed_venues(fnac_live_id)
    delete_all_physical_managed_venues(fnac_darty_participations_et_services_id)


def _change_venue(offer: Offer, target_venue_id: int) -> Offer:
    target_venue = Venue.query.filter_by(id=target_venue_id).one()
    offer.venue = target_venue
    return offer
