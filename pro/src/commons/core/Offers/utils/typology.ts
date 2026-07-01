import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'
import { isAllocineProvider } from '@/commons/core/Providers/utils/utils'

export const isOfferSynchronized = (
  offer?: GetIndividualOfferResponseModelV2 | null
): boolean => {
  if (!offer) {
    return false
  }
  return Boolean(offer.lastProvider)
}

export const isOfferAllocineSynchronized = (
  offer?: GetIndividualOfferResponseModelV2 | null
): boolean => {
  if (!offer) {
    return false
  }
  return isAllocineProvider(offer.lastProvider)
}

export const isOfferProductBased = (
  offer?: GetIndividualOfferResponseModelV2 | null
): boolean => {
  if (!offer) {
    return false
  }
  return Boolean(offer.productId) && !isOfferSynchronized(offer)
}
