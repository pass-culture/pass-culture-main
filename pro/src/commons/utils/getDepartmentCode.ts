import type {
  GetIndividualOfferResponseModelV2,
  ListOffersOfferResponseModel,
} from '@/apiClient/v1'

export const getDepartmentCode = (
  offer: GetIndividualOfferResponseModelV2 | ListOffersOfferResponseModel
): string => {
  return (offer.location?.departmentCode || offer.venue.departementCode) ?? ''
}
