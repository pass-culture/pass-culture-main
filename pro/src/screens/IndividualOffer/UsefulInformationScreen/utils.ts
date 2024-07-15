import {
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { CATEGORY_STATUS } from 'core/Offers/constants'

export const getFilteredVenueListBySubcategory = (
  venueList: VenueListItemResponseModel[],
  subcategory?: SubcategoryResponseModel
): VenueListItemResponseModel[] => {
  if (!subcategory) {
    return venueList
  }

  if (subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE) {
    return venueList
  }

  return venueList.filter((venue) =>
    subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
      ? venue.isVirtual
      : !venue.isVirtual
  )
}
