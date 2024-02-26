import { ListOffersResponseModel } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

export const serializeOffers = (offers: ListOffersResponseModel): Offer[] =>
  offers.map((offer) => ({
    ...offer,
  }))
