import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'

const filterCategories = (
  allCategories: IOfferCategory[],
  allSubCategories: IOfferSubCategory[],
  onlineOfflinePlatform: CATEGORY_STATUS
): [IOfferCategory[], IOfferSubCategory[]] => {
  const subCategories: IOfferSubCategory[] = allSubCategories.filter(
    (s: IOfferSubCategory) => {
      let excludedStatus
      if (onlineOfflinePlatform !== CATEGORY_STATUS.ONLINE_OR_OFFLINE) {
        excludedStatus =
          onlineOfflinePlatform === CATEGORY_STATUS.ONLINE
            ? CATEGORY_STATUS.OFFLINE
            : CATEGORY_STATUS.ONLINE
      }
      return (
        s.isSelectable &&
        (onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE ||
          s.onlineOfflinePlatform !== excludedStatus)
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
