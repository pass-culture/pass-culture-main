import { OfferStatus } from './constants/offerStatus'

export const isOfferDisabled = (status: OfferStatus): boolean => {
  return [
    OfferStatus.OFFER_STATUS_REJECTED,
    OfferStatus.OFFER_STATUS_PENDING,
  ].includes(status)
}
