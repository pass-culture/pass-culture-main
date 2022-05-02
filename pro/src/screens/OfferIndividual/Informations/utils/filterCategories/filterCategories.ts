import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'

import { CATEGORY_STATUS } from 'core/Offers'
import { TOfferIndividualVenue } from 'core/Venue/types'

const filterCategories = (
  allCategories: IOfferCategory[],
  allSubCategories: IOfferSubCategory[],
  venue?: TOfferIndividualVenue
): [categories: IOfferCategory[], subCategories: IOfferSubCategory[]] => {
  const subCategories: IOfferSubCategory[] = allSubCategories.filter(
    (s: IOfferSubCategory) => {
      const exludePlatformFilter = !venue
        ? null
        : venue.isVirtual
        ? CATEGORY_STATUS.OFFLINE
        : CATEGORY_STATUS.ONLINE
      return (
        s.isSelectable &&
        (exludePlatformFilter === null ||
          s.onlineOfflinePlatform !== exludePlatformFilter)
      )
    }
  )

  const categories: IOfferCategory[] = allCategories.filter(
    (c: IOfferCategory) => {
      const hasAvailableSubCategories =
        subCategories.filter((s: IOfferSubCategory) => s.categoryId === c.id)
          .length > 0
      return c.isSelectable && hasAvailableSubCategories
    }
  )

  return [categories, subCategories]
}

export default filterCategories
