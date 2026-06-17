import type { GetIndividualOfferResponseModel } from '@/apiClient/v1/new'

import { isAllocineProvider } from '../../Providers/utils/utils'

export const isOfferSynchronizedViaAllocine = (
  offer: GetIndividualOfferResponseModel | null | undefined = null
) => {
  return offer?.lastProvider ? isAllocineProvider(offer.lastProvider) : false
}
