import { useEffect, useState } from 'react'

import { CATEGORY_STATUS } from 'core/Offers'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'

export interface IUseFilteredCategoriesProps {
  allCategories: IOfferCategory[]
  allSubCategories: IOfferSubCategory[]
  onlineOfflinePlatform: CATEGORY_STATUS
}

type TFilteredCategories = [IOfferCategory[], IOfferSubCategory[]]

const buildFilteredCategories = ({
  allCategories,
  allSubCategories,
  onlineOfflinePlatform,
}: IUseFilteredCategoriesProps): TFilteredCategories => {
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

const useFilteredCategories = ({
  allCategories,
  allSubCategories,
  onlineOfflinePlatform,
}: IUseFilteredCategoriesProps): TFilteredCategories => {
  const [filteredCategories, setFilteredCategories] =
    useState<TFilteredCategories>(
      buildFilteredCategories({
        allCategories,
        allSubCategories,
        onlineOfflinePlatform,
      })
    )

  useEffect(() => {
    setFilteredCategories(
      buildFilteredCategories({
        allCategories,
        allSubCategories,
        onlineOfflinePlatform,
      })
    )
  }, [onlineOfflinePlatform])

  return filteredCategories
}

export default useFilteredCategories
