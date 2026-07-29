import type {
  GetIndividualOfferResponseModelV2,
  ListOffersOfferResponseModel,
} from '@/apiClient/v1'
import { OfferStatus } from '@/apiClient/v1'

export const isOfferDisabled = (
  offer: GetIndividualOfferResponseModelV2 | ListOffersOfferResponseModel
): boolean => {
  return [OfferStatus.REJECTED, OfferStatus.PENDING].includes(offer.status)
}
