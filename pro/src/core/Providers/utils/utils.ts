import { OfferIndividualVenueProvider } from 'core/Offers/types'

import { CINEMA_PROVIDER_NAMES } from '../constants'

/* istanbul ignore next: DEBT, TO FIX */
export const isAllocineProviderName = (
  providerName: string | null
): boolean => {
  if (providerName === null) {
    return false
  }
  return providerName.toLowerCase() === 'allociné'
}

/* istanbul ignore next: DEBT, TO FIX */
export const isCinemaProviderName = (providerName: string | null): boolean => {
  return (
    providerName !== null &&
    CINEMA_PROVIDER_NAMES.includes(providerName.toLowerCase())
  )
}

/* istanbul ignore next: DEBT, TO FIX */
export const isAllocineProvider = (
  provider?: OfferIndividualVenueProvider | null
): boolean => {
  if (!provider) {
    return false
  }
  return isAllocineProviderName(provider.name)
}

/* istanbul ignore next: DEBT, TO FIX */
export const isCinemaProvider = (
  provider?: OfferIndividualVenueProvider | null
): boolean => {
  if (!provider) {
    return false
  }
  return isCinemaProviderName(provider.name)
}
