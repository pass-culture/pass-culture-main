import type { GetIndividualOfferResponseModel } from '@/apiClient/v1'

export const isOfferSynchronized = (offer: GetIndividualOfferResponseModel) =>
  !!offer.lastProvider
