import type { ListOffersOfferResponseModel } from '@/apiClient/v1'
import type { GetIndividualOfferWithAddressResponseModel } from '@/apiClient/v1/new'

export const getDepartmentCode = (
  offer:
    | GetIndividualOfferWithAddressResponseModel
    | ListOffersOfferResponseModel
): string => {
  return (offer.location?.departmentCode || offer.venue.departementCode) ?? ''
}
