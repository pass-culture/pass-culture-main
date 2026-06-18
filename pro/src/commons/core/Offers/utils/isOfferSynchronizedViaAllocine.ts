import type { GetIndividualOfferResponseModelV2 } from '@/apiClient/v1'

import { isAllocineProvider } from '../../Providers/utils/utils'

export const isOfferSynchronizedViaAllocine = (
  offer: GetIndividualOfferResponseModelV2 | null | undefined = null
) => {
  return offer?.lastProvider ? isAllocineProvider(offer.lastProvider) : false
}
