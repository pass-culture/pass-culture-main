import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { TOfferIndividualVenue } from 'core/Venue/types'

const filterCategories = (
  allCategories: IOfferCategory[],
  allSubCategories: IOfferSubCategory[],
  venue?: TOfferIndividualVenue
): [categories: IOfferCategory[], subCategories: IOfferSubCategory[]] => {
  const subCategories: IOfferSubCategory[] = allSubCategories.filter(
    (s: IOfferSubCategory) => {
      let excludedStatus
      if (venue) {
        excludedStatus = venue.isVirtual
          ? CATEGORY_STATUS.OFFLINE
          : CATEGORY_STATUS.ONLINE
      }
      return (
        s.isSelectable &&
        (venue === undefined || s.onlineOfflinePlatform !== excludedStatus)
      )
    }
  )

  const categories: IOfferCategory[] = allCategories.filter(
    (c: IOfferCategory) =>
      c.isSelectable &&
      subCategories.filter((s: IOfferSubCategory) => s.categoryId === c.id)
        .length > 0
  )

  return [categories, subCategories]
}

export default filterCategories
