import { isAllocineProvider } from 'core/Providers'

import { IndividualOffer } from '../types'

export const isOfferSynchronized = (
  offer?: IndividualOffer | null
): boolean => {
  if (!offer) {
    return false
  }
  return Boolean(offer.lastProvider)
}

export const isOfferAllocineSynchronized = (
  offer?: IndividualOffer | null
): boolean => {
  if (!offer) {
    return false
  }
  return isAllocineProvider(offer.lastProvider)
}
