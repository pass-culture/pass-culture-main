import { useEffect, useState } from 'react'

import { IOfferSubCategory } from 'core/Offers/types'

const buildSubcategoryOptions = (
  subCategories: IOfferSubCategory[],
  categoryId: string
) => {
  return subCategories
    .filter((s: IOfferSubCategory) => s.categoryId === categoryId)
    .map((s: IOfferSubCategory) => ({
      value: s.id,
      label: s.proLabel,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
}

const useSubcategoryOptions = (
  subCategories: IOfferSubCategory[],
  categoryId: string
): SelectOptions => {
  const [subcategoryOptions, setSubcategoryOptions] = useState<SelectOptions>(
    buildSubcategoryOptions(subCategories, categoryId)
  )

  useEffect(() => {
    setSubcategoryOptions(buildSubcategoryOptions(subCategories, categoryId))
  }, [categoryId])

  return subcategoryOptions
}

export default useSubcategoryOptions
