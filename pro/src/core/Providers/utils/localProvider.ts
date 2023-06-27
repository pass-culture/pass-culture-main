import { OfferIndividual } from 'core/Offers/types'
import { isAllocineProvider } from 'core/Providers'

export const isAllocineOffer = (
  offer: OfferIndividual | null | undefined = null
) => {
  return offer?.lastProvider ? isAllocineProvider(offer?.lastProvider) : false
}
