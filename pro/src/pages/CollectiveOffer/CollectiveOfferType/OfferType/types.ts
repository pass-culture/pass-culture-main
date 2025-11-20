import type {
  COLLECTIVE_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
} from '@/commons/core/Offers/constants'

export interface OfferTypeFormValues {
  offer: {
    collectiveOfferSubtype: COLLECTIVE_OFFER_SUBTYPE
    collectiveOfferSubtypeDuplicate: COLLECTIVE_OFFER_SUBTYPE_DUPLICATE
  }
}
