import {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  INDIVIDUAL_OFFER_SUBTYPE,
  OFFER_TYPES,
} from 'commons/core/Offers/constants'

export interface OfferTypeFormValues {
  offer: {
    offerType: OFFER_TYPES
    collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE
    collectiveOfferSubtypeDuplicate: COLLECTIVE_OFFER_SUBTYPE_DUPLICATE
    individualOfferSubtype: INDIVIDUAL_OFFER_SUBTYPE
  }
}
