import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

export const serializeOffers = (
  offers: CollectiveOfferResponseModel[]
): Offer[] =>
  offers.map((offer) => ({
    ...offer,
    thumbUrl: offer.imageUrl,
    isEducational: true,
    isEvent: true,
    productIsbn: null,
    educationalBooking: offer.booking,
  }))
