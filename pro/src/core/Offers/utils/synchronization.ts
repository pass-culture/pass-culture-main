import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { isAllocineProvider } from 'core/Providers'

export const isOfferSynchronized = (
  offer?: GetIndividualOfferResponseModel | null
): boolean => {
  if (!offer) {
    return false
  }
  return Boolean(offer.lastProvider)
}

export const isOfferAllocineSynchronized = (
  offer?: GetIndividualOfferResponseModel | null
): boolean => {
  if (!offer) {
    return false
  }
  return isAllocineProvider(offer.lastProvider)
}
