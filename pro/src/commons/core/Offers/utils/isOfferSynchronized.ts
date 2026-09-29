import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'

export const isOfferSynchronized = (offer: GetIndividualOfferResponseModelV2) =>
  !!offer.lastProvider
