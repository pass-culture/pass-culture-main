import type {
  GetIndividualOfferWithAddressResponseModel,
  GetVenueResponseModel,
  ListOffersOfferResponseModel,
} from '@/apiClient/v1'

export const getDepartmentCode = (
  offer:
    | GetIndividualOfferWithAddressResponseModel
    | ListOffersOfferResponseModel,
  venue: GetVenueResponseModel
): string => {
  return (offer.location?.departmentCode || venue.location.departmentCode) ?? ''
}
