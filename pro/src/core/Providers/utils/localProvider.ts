import { IOfferIndividual } from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

export const isAllocineOffer = (
  offer: IOfferIndividual | null | undefined = null
) => {
  return offer?.lastProvider ? isAllocineProvider(offer?.lastProvider) : false
}
