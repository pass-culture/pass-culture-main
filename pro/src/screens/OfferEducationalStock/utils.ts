import { OfferStatus } from 'custom_types/offer'

export const isOfferDisabled = (status: OfferStatus): boolean => {
  return [
    OfferStatus.OFFER_STATUS_REJECTED,
    OfferStatus.OFFER_STATUS_PENDING,
  ].includes(status)
}
