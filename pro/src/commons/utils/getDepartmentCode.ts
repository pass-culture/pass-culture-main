import {
  GetIndividualOfferWithAddressResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'

export const getDepartmentCode = (
  offer:
    | GetIndividualOfferWithAddressResponseModel
    | ListOffersOfferResponseModel
): string => {
  return (offer.address?.departmentCode || offer.venue.departementCode) ?? ''
}
