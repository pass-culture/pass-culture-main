import { CollectiveOfferStatus, OfferStatus } from 'apiClient/v1'

// FIXME(anoukhello - 2024-06-21) remove this function for collective offers as it is
// redundant with the attribute isEditable on collective offer
export const isOfferDisabled = (
  status: OfferStatus | CollectiveOfferStatus
): boolean => {
  return [
    OfferStatus.REJECTED,
    OfferStatus.PENDING,
    CollectiveOfferStatus.REJECTED,
    CollectiveOfferStatus.PENDING,
  ].includes(status)
}
