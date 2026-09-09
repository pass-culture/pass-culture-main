import type {
  GetIndividualOfferResponseModel,
  GetVenueResponseModel,
  ListOffersOfferResponseModel,
} from '@/apiClient/v1'

export const getDepartmentCode = (
  offer: GetIndividualOfferResponseModel | ListOffersOfferResponseModel,
  venue: GetVenueResponseModel
): string => {
  return (offer.location?.departmentCode || venue.location.departmentCode) ?? ''
}
