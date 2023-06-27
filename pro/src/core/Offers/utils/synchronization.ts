import { isAllocineProvider } from 'core/Providers'

import { OfferIndividual } from '../types'

export const isOfferSynchronized = (
  offer?: OfferIndividual | null
): boolean => {
  if (!offer) {
    return false
  }
  return Boolean(offer.lastProvider)
}

export const isOfferAllocineSynchronized = (
  offer?: OfferIndividual | null
): boolean => {
  if (!offer) {
    return false
  }
  return isAllocineProvider(offer.lastProvider)
}
