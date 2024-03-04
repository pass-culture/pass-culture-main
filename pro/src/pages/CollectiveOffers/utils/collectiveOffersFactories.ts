import {
  CollectiveOfferResponseModel,
  ListOffersVenueResponseModel,
  OfferStatus,
} from 'apiClient/v1'

let offerId = 1

export const collectiveOfferFactory = (
  customCollectiveOffer: Partial<CollectiveOfferResponseModel> = {}
): CollectiveOfferResponseModel => {
  const currentId = offerId++

  return {
    id: currentId,
    status: OfferStatus.ACTIVE,
    isActive: true,
    hasBookingLimitDatetimesPassed: true,
    isEducational: true,
    name: `offer name ${offerId}`,
    venue: listOffersVenueFactory(),
    stocks: [],
    isEditable: true,
    isPublicApi: false,
    interventionArea: [],
    isShowcase: false,
    ...customCollectiveOffer,
  }
}

export const listOffersVenueFactory = (
  customListOffersVenue: Partial<ListOffersVenueResponseModel> = {}
): ListOffersVenueResponseModel => ({
  id: 1,
  name: 'venue name',
  offererName: 'offerer name',
  isVirtual: false,
  ...customListOffersVenue,
})
