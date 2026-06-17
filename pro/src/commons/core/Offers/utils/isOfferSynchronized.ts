import type { GetIndividualOfferResponseModel } from '@/apiClient/v1/new'

export const isOfferSynchronized = (offer: GetIndividualOfferResponseModel) =>
  !!offer.lastProvider
