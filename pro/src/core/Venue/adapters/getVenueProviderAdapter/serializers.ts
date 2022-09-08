import { VenueProviderResponse } from 'apiClient/v1'

import { IVenueProviderApi } from '../../types'

export const serializeVenueProvidersApi = (
  venueProviders: VenueProviderResponse[]
): IVenueProviderApi[] => {
  return venueProviders.map(venueProvider => ({
    id: venueProvider.id,
    idAtProviders: venueProvider.idAtProviders || null,
    dateModifiedAtLastProvider:
      venueProvider.dateModifiedAtLastProvider || null,
    isActive: venueProvider.isActive,
    isFromAllocineProvider: venueProvider.isFromAllocineProvider,
    lastProviderId: venueProvider.lastProviderId || null,
    lastSyncDate: venueProvider.lastSyncDate || null,
    nOffers: venueProvider.nOffers,
    providerId: venueProvider.providerId,
    venueId: venueProvider.venueId,
    venueIdAtOfferProvider: venueProvider.venueIdAtOfferProvider,
    provider: {
      name: venueProvider.provider.name,
      enabledForPro: venueProvider.provider.enabledForPro,
      id: venueProvider.provider.id,
      isActive: venueProvider.provider.isActive,
      localClass: venueProvider.provider.localClass,
    },
    quantity: venueProvider.quantity,
    isDuo: venueProvider.isDuo || null,
    price: venueProvider.price || 0,
  }))
}
