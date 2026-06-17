import type {
  GetIndividualOfferResponseModel,
  ListOffersOfferResponseModel,
} from '@/apiClient/v1/new'
import { OfferStatus } from '@/apiClient/v1/new'

export const isOfferDisabled = (
  offer: GetIndividualOfferResponseModel | ListOffersOfferResponseModel
): boolean => {
  return [OfferStatus.REJECTED, OfferStatus.PENDING].includes(offer.status)
}
