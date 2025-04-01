import { PriceCategoryResponseModel } from 'apiClient/v1'
import { SelectOption } from 'commons/custom_types/form'
import { formatPrice } from 'commons/utils/formatPrice'

export const getPriceCategoryOptions = (
  priceCategories?: PriceCategoryResponseModel[] | null
): SelectOption[] => {
  // Clone list to avoid mutation
  const newPriceCategories = [...(priceCategories ?? [])]
  newPriceCategories.sort((a, b) => {
    if (a.price === b.price) {
      return a.label.localeCompare(b.label)
    }
    return a.price - b.price
  })

  return newPriceCategories.map(
    (priceCategory): SelectOption => ({
      label: getPriceCategoryName(priceCategory),
      value: priceCategory.id,
    })
  )
}

export function getPriceCategoryName(
  priceCategory: PriceCategoryResponseModel
) {
  return `${formatPrice(priceCategory.price)} - ${priceCategory.label}`
}
