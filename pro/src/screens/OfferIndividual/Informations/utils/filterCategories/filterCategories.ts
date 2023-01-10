import { CATEGORY_STATUS, INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { parse } from 'utils/query-string'

export const getOfferSubtypeFromParams = (
  queryParams: string
): INDIVIDUAL_OFFER_SUBTYPE | null => {
  const params = parse(queryParams)

  switch (params['offer-type']) {
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
      return null
  }
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

const isSubcategoryMatchingCriteria = (
  subcategory: IOfferSubCategory,
  onlineOfflinePlatform: CATEGORY_STATUS
) => {
  if (onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE) {
    return true
  }

  return (
    subcategory.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE ||
    subcategory.onlineOfflinePlatform === onlineOfflinePlatform
  )
}

const filterCategories = (
  allCategories: IOfferCategory[],
  allSubCategories: IOfferSubCategory[],
  onlineOfflinePlatform: CATEGORY_STATUS
): [IOfferCategory[], IOfferSubCategory[]] => {
  const subCategories: IOfferSubCategory[] = allSubCategories.filter(
    (subcategory: IOfferSubCategory) => {
      if (!subcategory.isSelectable) {
        return false
      }

      return isSubcategoryMatchingCriteria(subcategory, onlineOfflinePlatform)
    }
  )
  const categories: IOfferCategory[] = allCategories.filter(
    (c: IOfferCategory) =>
      c.isSelectable &&
      subCategories.some((s: IOfferSubCategory) => s.categoryId === c.id)
  )

  return [categories, subCategories]
}

export default filterCategories
