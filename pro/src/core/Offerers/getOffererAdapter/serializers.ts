import { GetOffererResponseModel } from 'apiClient/v1'

import { Offerer } from '../types'

export const serializeOffererApi = (
  offerer: GetOffererResponseModel
): Offerer => {
  return <Offerer>{
    ...offerer,
    address: offerer.address || '',
    demarchesSimplifieesApplicationId:
      offerer.demarchesSimplifieesApplicationId || '',
    hasAvailablePricingPoints: offerer.hasAvailablePricingPoints || undefined,
    hasDigitalVenueAtLeastOneOffer:
      offerer.hasDigitalVenueAtLeastOneOffer || undefined,
    isValidated: offerer.isValidated || undefined,
    isActive: offerer.isActive || undefined,
  }
}
