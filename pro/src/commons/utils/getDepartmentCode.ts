import type {
  GetIndividualOfferWithAddressResponseModel,
  ListOffersOfferResponseModel,
} from '@/apiClient/v1'

export const getDepartmentCode = (
  offer:
    | GetIndividualOfferWithAddressResponseModel
    | ListOffersOfferResponseModel
): string => {
  return (offer.location?.departmentCode || offer.venue.departementCode) ?? ''
}
