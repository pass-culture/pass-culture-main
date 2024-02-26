import { CollectiveOfferResponseModel } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

export const serializeOffers = (
  offers: CollectiveOfferResponseModel[]
): Offer[] =>
  offers.map((offer) => ({
    id: offer.id,
    status: offer.status,
    isActive: offer.isActive,
    hasBookingLimitDatetimesPassed: offer.hasBookingLimitDatetimesPassed,
    thumbUrl: offer.imageUrl,
    isEducational: true,
    name: offer.name,
    isEvent: true,
    productIsbn: null,
    venue: offer.venue,
    stocks: offer.stocks,
    isPublicApi: offer.isPublicApi,
    isEditable: offer.isEditable,
    isShowcase: offer.isShowcase,
    educationalInstitution: offer.educationalInstitution,
    educationalBooking: offer.booking,
  }))
