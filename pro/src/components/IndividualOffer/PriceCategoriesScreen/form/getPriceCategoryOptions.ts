import type { PriceCategoryResponseModel } from '@/apiClient/v1'
import type { SelectOption } from '@/commons/custom_types/form'
import { convertEuroToPacificFranc, formatPacificFranc } from '@/commons/utils/convertEuroToPacificFranc'
import { formatPrice } from '@/commons/utils/formatPrice'

export const getPriceCategoryOptions = (
  priceCategories?: PriceCategoryResponseModel[] | null,
  isCaledonian: boolean = false
): SelectOption<number>[] => {
  // Clone list to avoid mutation
  const newPriceCategories = [...(priceCategories ?? [])]
  newPriceCategories.sort((a, b) => {
    if (a.price === b.price) {
      return a.label.localeCompare(b.label)
    }
    return a.price - b.price
  })

  return newPriceCategories.map(
    (priceCategory): SelectOption<number> => ({
      label: getPriceCategoryName(priceCategory, isCaledonian),
      value: priceCategory.id,
    })
  )
}

export function getPriceCategoryName(
  priceCategory: PriceCategoryResponseModel,
  isCaledonian: boolean = false
) {
  return `${isCaledonian ? formatPacificFranc(convertEuroToPacificFranc(priceCategory.price)) : formatPrice(priceCategory.price)} - ${priceCategory.label}`
}
