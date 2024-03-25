import { PriceCategoryResponseModel } from 'apiClient/v1'
import { SelectOption } from 'custom_types/form'
import { formatPrice } from 'utils/formatPrice'

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
      label: `${formatPrice(priceCategory.price)} - ${priceCategory.label}`,
      value: priceCategory.id,
    })
  )
}
