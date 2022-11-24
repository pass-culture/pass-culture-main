import { OfferStatus } from 'apiClient/v1'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from 'core/Offers/constants'

export const isOfferDisabled = (status: OfferStatus) => {
  return [OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(status)
}
