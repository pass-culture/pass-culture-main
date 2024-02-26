import { ListOffersVenueResponseModel, OfferStatus } from 'apiClient/v1'
import { Offer } from 'core/Offers/types'

let offerId = 1

export const collectiveOfferFactory = (customOffer = {}): Offer => {
  const currentId = offerId++
  return {
    id: currentId,
    status: OfferStatus.ACTIVE,
    isActive: true,
    hasBookingLimitDatetimesPassed: true,
    isEducational: false,
    name: `offer name ${offerId}`,
    isEvent: true,
    venue: venueFactory(),
    stocks: [],
    isEditable: true,
    isPublicApi: false,
    ...customOffer,
  }
}

export const venueFactory = (
  customVenue: Partial<ListOffersVenueResponseModel> = {}
): ListOffersVenueResponseModel => ({
  id: 1,
  name: 'venue name',
  offererName: 'offerer name',
  isVirtual: false,
  ...customVenue,
})
