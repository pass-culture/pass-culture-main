import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'core/Offers/constants'

export const getOfferSubtypeFromParam = (
  offerType: string | null | undefined
): INDIVIDUAL_OFFER_SUBTYPE | null => {
  switch (offerType) {
    // This is stupid but there is no simple way to cast string to enums
    // while checking that the values are valid (`as` is a bad solution)
    case INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD:
      return INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
    case INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD:
      return INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
    case INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT:
      return INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT
    case INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT:
      return INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
    default:
  }

  // If the parameter is not set, we don't filter
  return null
}

export const getCategoryStatusFromOfferSubtype = (
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE | null
): CATEGORY_STATUS => {
  if (offerSubtype === null) {
    return CATEGORY_STATUS.ONLINE_OR_OFFLINE
  }

  return offerSubtype === INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT ||
    offerSubtype === INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
    ? CATEGORY_STATUS.ONLINE
    : CATEGORY_STATUS.OFFLINE
}

export const isOfferSubtypeEvent = (
  offerSubtype: INDIVIDUAL_OFFER_SUBTYPE | null
): boolean | null => {
  if (offerSubtype === null) {
    return null
  }
  return (
    offerSubtype === INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT ||
    offerSubtype === INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
  )
}

const isSubcategoryMatchingCriteria = (
  subcategory: SubcategoryResponseModel,
  onlineOfflinePlatform: CATEGORY_STATUS,
  isEvent: boolean | null
) => {
  if (isEvent !== null && subcategory.isEvent !== isEvent) {
    return false
  }

  if (onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE) {
    return true
  }

  return (
    subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE ||
    subcategory.onlineOfflinePlatform === onlineOfflinePlatform
  )
}

export const filterCategories = (
  allCategories: CategoryResponseModel[],
  allSubCategories: SubcategoryResponseModel[],
  onlineOfflinePlatform: CATEGORY_STATUS,
  isEvent: boolean | null
): [CategoryResponseModel[], SubcategoryResponseModel[]] => {
  const subCategories: SubcategoryResponseModel[] = allSubCategories.filter(
    (subcategory: SubcategoryResponseModel) => {
      if (!subcategory.isSelectable) {
        return false
      }

      return isSubcategoryMatchingCriteria(
        subcategory,
        onlineOfflinePlatform,
        isEvent
      )
    }
  )
  const categories: CategoryResponseModel[] = allCategories.filter(
    (c: CategoryResponseModel) =>
      c.isSelectable &&
      subCategories.some((s: SubcategoryResponseModel) => s.categoryId === c.id)
  )

  return [categories, subCategories]
}
