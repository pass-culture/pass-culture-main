import { isAllocineProvider } from 'core/Providers'

import { IOfferIndividual } from '../types'

export const isOfferSynchronized = (
  offer?: IOfferIndividual | null
): boolean => {
  if (!offer) return false
  return Boolean(offer.lastProvider)
}

export const isOfferAllocineSynchronized = (
  offer?: IOfferIndividual | null
): boolean => {
  if (!offer) return false
  return isAllocineProvider(offer.lastProvider)
}
