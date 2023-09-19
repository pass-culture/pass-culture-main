import {
  CATEGORY_STATUS,
  INDIVIDUAL_OFFER_SUBTYPE,
} from 'core/Offers/constants'
import { OfferCategory, OfferSubCategory } from 'core/Offers/types'

export const getOfferSubtypeFromParam = (
  offerType: string | null
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
  subcategory: OfferSubCategory,
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

const filterCategories = (
  allCategories: OfferCategory[],
  allSubCategories: OfferSubCategory[],
  onlineOfflinePlatform: CATEGORY_STATUS,
  isEvent: boolean | null
): [OfferCategory[], OfferSubCategory[]] => {
  const subCategories: OfferSubCategory[] = allSubCategories.filter(
    (subcategory: OfferSubCategory) => {
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
  const categories: OfferCategory[] = allCategories.filter(
    (c: OfferCategory) =>
      c.isSelectable &&
      subCategories.some((s: OfferSubCategory) => s.categoryId === c.id)
  )

  return [categories, subCategories]
}

export default filterCategories
