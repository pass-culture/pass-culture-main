import { OFFER_STATUS } from 'components/pages/Offers/Offers/domain/offerStatus'

export const isOfferDisabled = status => {
  return [OFFER_STATUS.REJECTED, OFFER_STATUS.AWAITING].includes(status)
}
