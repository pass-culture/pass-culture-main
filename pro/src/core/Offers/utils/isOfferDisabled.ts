import { OfferStatus } from 'apiClient/v1'

export const isOfferDisabled = (status: OfferStatus) => {
  return [OfferStatus.REJECTED, OfferStatus.PENDING].includes(status)
}
