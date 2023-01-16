import { CATEGORY_STATUS, INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers'
import {
  IOfferCategory,
  IOfferIndividual,
  IOfferSubCategory,
} from 'core/Offers/types'
import { parse } from 'utils/query-string'

export const getOfferSubtypeFromParamsOrOffer = (
  queryParams: string,
  offer: IOfferIndividual | null
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
  }

  // If the parameter is not set, try to guess the subtype from the offer object
  if (offer === null) {
    return null
  }

  if (offer.isDigital) {
    return offer.isEvent
      ? INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
      : INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
  } else {
    return offer.isEvent
      ? INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT
      : INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
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
  subcategory: IOfferSubCategory,
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
  allCategories: IOfferCategory[],
  allSubCategories: IOfferSubCategory[],
  onlineOfflinePlatform: CATEGORY_STATUS,
  isEvent: boolean | null
): [IOfferCategory[], IOfferSubCategory[]] => {
  const subCategories: IOfferSubCategory[] = allSubCategories.filter(
    (subcategory: IOfferSubCategory) => {
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
  const categories: IOfferCategory[] = allCategories.filter(
    (c: IOfferCategory) =>
      c.isSelectable &&
      subCategories.some((s: IOfferSubCategory) => s.categoryId === c.id)
  )

  return [categories, subCategories]
}

export default filterCategories
