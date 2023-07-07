import { GetOffererResponseModel } from 'apiClient/v1'

import { Offerer } from '../types'

export const serializeOffererApi = (
  offerer: GetOffererResponseModel
): Offerer => {
  return <Offerer>{
    address: offerer.address || '',
    apiKey: offerer.apiKey || null,
    city: offerer.city || '',
    dateCreated: offerer.dateCreated || '',
    demarchesSimplifieesApplicationId:
      offerer.demarchesSimplifieesApplicationId || '',
    hasAvailablePricingPoints: offerer.hasAvailablePricingPoints || undefined,
    hasDigitalVenueAtLeastOneOffer:
      offerer.hasDigitalVenueAtLeastOneOffer || undefined,
    isValidated: offerer.isValidated || undefined,
    isActive: offerer.isActive || undefined,
    name: offerer.name || '',
    id: offerer.id || 0,
    postalCode: offerer.postalCode || '',
    siren: offerer.siren || '',
    managedVenues: offerer.managedVenues || [],
  }
}
