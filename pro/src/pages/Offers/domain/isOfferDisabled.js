import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'

export const isOfferDisabled = status => {
  return [OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(status)
}
