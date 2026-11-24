import type {
  GetIndividualOfferResponseModelV2,
  GetVenueResponseModel,
  ListOffersOfferResponseModel,
} from '@/apiClient/v1'

export const getDepartmentCode = (
  offer: GetIndividualOfferResponseModelV2 | ListOffersOfferResponseModel,
  venue: GetVenueResponseModel
): string => {
  return (offer.location?.departmentCode || venue.location.departmentCode) ?? ''
}
