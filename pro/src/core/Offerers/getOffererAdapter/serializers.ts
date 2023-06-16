import { GetOffererResponseModel } from 'apiClient/v1'

import { IOfferer } from '../types'

export const serializeOffererApi = (
  offerer: GetOffererResponseModel
): IOfferer => {
  return <IOfferer>{
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
    nonHumanizedId: offerer.nonHumanizedId || 0,
    postalCode: offerer.postalCode || '',
    siren: offerer.siren || '',
    managedVenues: offerer.managedVenues || [],
  }
}
