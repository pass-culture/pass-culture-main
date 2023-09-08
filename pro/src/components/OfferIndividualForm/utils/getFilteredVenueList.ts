import { CATEGORY_STATUS } from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'
import { OfferIndividualVenue } from 'core/Venue/types'

export const getFilteredVenueListBySubcategory = (
  venueList: OfferIndividualVenue[],
  subcategory?: OfferSubCategory
): OfferIndividualVenue[] => {
  if (!subcategory) {
    return venueList
  }

  if (
    subcategory?.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE
  ) {
    return venueList
  }

  return venueList.filter(venue =>
    subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
      ? venue.isVirtual
      : !venue.isVirtual
  )
}

export const getFilteredVenueListByCategoryStatus = (
  venueList: OfferIndividualVenue[],
  categoryStatus: CATEGORY_STATUS
): OfferIndividualVenue[] => {
  if (categoryStatus === CATEGORY_STATUS.ONLINE_OR_OFFLINE) {
    return venueList
  }

  return venueList.filter(venue =>
    categoryStatus === CATEGORY_STATUS.ONLINE
      ? venue.isVirtual
      : !venue.isVirtual
  )
}
