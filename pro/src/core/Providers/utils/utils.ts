import { IOfferIndividualVenueProvider } from 'core/Offers/types'

import { CINEMA_PROVIDER_NAMES } from '../constants'

/* istanbul ignore next: DEBT, TO FIX */
export const isAllocineProvider = (
  provider: IOfferIndividualVenueProvider | null
): boolean => {
  if (provider === null) {
    return false
  }
  return provider.name.toLowerCase() === 'allociné'
}

/* istanbul ignore next: DEBT, TO FIX */
export const isCinemaProvider = (
  provider: IOfferIndividualVenueProvider | null
): boolean => {
  if (provider === null) {
    return false
  }
  return CINEMA_PROVIDER_NAMES.includes(provider?.name.toLowerCase())
}
