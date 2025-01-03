import {
  GetIndividualOfferWithAddressResponseModel,
  ListOffersOfferResponseModel,
} from 'apiClient/v1'

export const getDepartmentCode = ({
  offer,
  useOffererAddressAsDataSourceEnabled,
}: {
  offer:
    | GetIndividualOfferWithAddressResponseModel
    | ListOffersOfferResponseModel
  useOffererAddressAsDataSourceEnabled: boolean
}): string => {
  return offer.address?.departmentCode && useOffererAddressAsDataSourceEnabled
    ? offer.address.departmentCode
    : (offer.venue.departementCode ?? '')
}
