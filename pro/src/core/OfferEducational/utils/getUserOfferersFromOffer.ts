import { GetEducationalOffererResponseModel } from 'apiClient/v1'

import { CollectiveOffer, CollectiveOfferTemplate } from '../types'

export const getUserOfferersFromOffer = (
  offerers: GetEducationalOffererResponseModel[],
  offer?: CollectiveOffer | CollectiveOfferTemplate
): GetEducationalOffererResponseModel[] => {
  if (offer === undefined) {
    return offerers
  }

  const userOfferers = offerers.filter(offerer =>
    offerer.managedVenues.map(venue => venue.id).includes(offer.venue.id)
  )

  return userOfferers
}
