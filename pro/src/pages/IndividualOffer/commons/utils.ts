import type { GetIndividualOfferResponseModel, SubcategoryResponseModel } from "apiClient/v1"
import { CATEGORY_STATUS } from "commons/core/Offers/constants"

export const isOfferSubcategoryOnline = (offer: GetIndividualOfferResponseModel, subcategories: SubcategoryResponseModel[]): boolean => {
  // TODO (igabriele, 2025-07-25): Use `hasUrl` once `isDigital` is renamed to `hasUrl` in the API / model.
  const hasUrl = Boolean(offer.url?.trim())
  if (hasUrl) {
    return true
  }

  const subcategory = subcategories.find(
    (subcategory) => subcategory.id === offer.subcategoryId
  )

  return subcategory?.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
}
