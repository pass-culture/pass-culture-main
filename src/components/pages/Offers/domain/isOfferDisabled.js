import {
  OFFER_STATUS_AWAITING,
  OFFER_STATUS_REJECTED,
} from 'components/pages/Offers/Offers/_constants'

export const isOfferDisabled = status => {
  return [OFFER_STATUS_REJECTED, OFFER_STATUS_AWAITING].includes(status)
}
