export interface IVenueProviderApi {
  id: string
  idAtProviders: string | null
  dateModifiedAtLastProvider: string | null
  isActive: boolean
  isFromAllocineProvider: boolean
  lastProviderId: string | null
  lastSyncDate: string | null
  nOffers: number
  providerId: string
  venueId: string
  venueIdAtOfferProvider: string
  provider: any
  quantity?: number
  isDuo: boolean | null
  price: number
}
