import { OFFER_STATUS } from './offerStatus'

export const computeOfferStatus = offer => {
  switch (offer.status) {
    case 'EXPIRED':
      return OFFER_STATUS.EXPIRED
    case 'SOLD_OUT':
      return OFFER_STATUS.SOLD_OUT
    case 'ACTIVE':
      return OFFER_STATUS.ACTIVE
    case 'REJECTED':
      return OFFER_STATUS.REJECTED
    case 'AWAITING':
      return OFFER_STATUS.AWAITING
    case 'VALIDATED':
      return OFFER_STATUS.VALIDATED
    default:
      return OFFER_STATUS.VALIDATED
  }
}
