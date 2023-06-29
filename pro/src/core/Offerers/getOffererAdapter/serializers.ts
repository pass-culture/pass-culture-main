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
    dateModifiedAtLastProvider: offerer.dateModifiedAtLastProvider || '',
    demarchesSimplifieesApplicationId:
      offerer.demarchesSimplifieesApplicationId || '',
    fieldsUpdated: offerer.fieldsUpdated || [],
    hasAvailablePricingPoints: offerer.hasAvailablePricingPoints || undefined,
    hasDigitalVenueAtLeastOneOffer:
      offerer.hasDigitalVenueAtLeastOneOffer || undefined,
    idAtProviders: offerer.idAtProviders || '',
    isValidated: offerer.isValidated || undefined,
    isActive: offerer.isActive || undefined,
    lastProviderId: offerer.lastProviderId || '',
    name: offerer.name || '',
    id: offerer.id || 0,
    postalCode: offerer.postalCode || '',
    siren: offerer.siren || '',
    managedVenues: offerer.managedVenues || [],
  }
}
