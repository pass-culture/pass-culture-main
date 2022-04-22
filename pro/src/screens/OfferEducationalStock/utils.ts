import { OfferStatus } from 'api/v1/gen'

export const isOfferDisabled = (status: OfferStatus): boolean => {
  return [OfferStatus.REJECTED, OfferStatus.PENDING].includes(status)
}
