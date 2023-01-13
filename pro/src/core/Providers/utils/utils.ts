import { IOfferIndividualVenueProvider } from 'core/Offers/types'

import { CINEMA_PROVIDER_NAMES } from '../constants'

export const isAllocineProviderName = (
  providerName: string | null
): boolean => {
  if (providerName === null) {
    return false
  }
  return providerName.toLowerCase() === 'allociné'
}

export const isCinemaProviderName = (providerName: string | null): boolean => {
  return (
    providerName !== null &&
    CINEMA_PROVIDER_NAMES.includes(providerName.toLowerCase())
  )
}

export const isAllocineProvider = (
  provider?: IOfferIndividualVenueProvider | null
): boolean => {
  if (!provider) {
    return false
  }
  return isAllocineProviderName(provider.name)
}

export const isCinemaProvider = (
  provider?: IOfferIndividualVenueProvider | null
): boolean => {
  if (!provider) {
    return false
  }
  return isCinemaProviderName(provider.name)
}
