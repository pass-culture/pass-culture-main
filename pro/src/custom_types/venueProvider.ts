export type VenueProviderPayload = {
  venueId: string
  providerId: string
  venueIdAtOfferProvider?: string
  price?: string
  isDuo?: boolean
  quantity?: number
}

export type VenueProvider = {
  id: string
  idAtProviders?: string
  dateModifiedAtLastProvider?: Date
  isActive: boolean
  isFromAllocineProvider: boolean
  lastProviderId?: string
  lastSyncDate?: Date
  nOffers: number
  providerId: string
  venueId: string
  venueIdAtOfferProvider: string
  provider: {
    name: string
    enabledForPro: boolean
    id: string
    isActive: boolean
    localClass?: string
  }
  fieldsUpdated: string
  quantity?: number
  isDuo?: boolean
  price?: number
}
