import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'

const filterCategories = (
  allCategories: IOfferCategory[],
  allSubCategories: IOfferSubCategory[],
  onlineOfflinePlatform: CATEGORY_STATUS
): [IOfferCategory[], IOfferSubCategory[]] => {
  const subCategories: IOfferSubCategory[] = allSubCategories.filter(
    (s: IOfferSubCategory) => {
      if (onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE) {
        return s.isSelectable
      }

      return (
        s.isSelectable &&
        (s.onlineOfflinePlatform === CATEGORY_STATUS.ONLINE_OR_OFFLINE ||
          s.onlineOfflinePlatform === onlineOfflinePlatform)
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
