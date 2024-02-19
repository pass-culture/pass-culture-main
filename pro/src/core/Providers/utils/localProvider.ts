import { GetIndividualOfferResponseModel } from 'apiClient/v1'
import { isAllocineProvider } from 'core/Providers'

export const isAllocineOffer = (
  offer: GetIndividualOfferResponseModel | null | undefined = null
) => {
  return offer?.lastProvider ? isAllocineProvider(offer?.lastProvider) : false
}
