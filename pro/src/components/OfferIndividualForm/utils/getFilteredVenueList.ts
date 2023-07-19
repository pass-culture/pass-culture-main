import { CATEGORY_STATUS } from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'
import { OfferIndividualVenue } from 'core/Venue/types'

export const getFilteredVenueList = (
  subcategoryId: string,
  subCategories: OfferSubCategory[],
  venueList: OfferIndividualVenue[]
): OfferIndividualVenue[] => {
  if (!subcategoryId) {
    return venueList
  }

  const subCategory = subCategories.find(s => s.id === subcategoryId)
  if (
    !subCategory ||
    subCategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE
  ) {
    return venueList
  }

  return venueList.filter(venue =>
    subCategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
      ? venue.isVirtual
      : !venue.isVirtual
  )
}
