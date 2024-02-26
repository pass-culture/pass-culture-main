import {
  CollectiveOfferResponseModel,
  ListOffersVenueResponseModel,
  OfferStatus,
} from 'apiClient/v1'

let offerId = 1

export const collectiveOfferFactory = (
  customOffer: Partial<CollectiveOfferResponseModel> = {}
): CollectiveOfferResponseModel => {
  const currentId = offerId++

  return {
    id: currentId,
    status: OfferStatus.ACTIVE,
    isActive: true,
    hasBookingLimitDatetimesPassed: true,
    isEducational: true,
    name: `offer name ${offerId}`,
    venue: venueFactory(),
    stocks: [],
    isEditable: true,
    isPublicApi: false,
    interventionArea: [],
    isShowcase: false,
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
