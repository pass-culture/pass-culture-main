import { SubcategoryResponseModel } from 'apiClient/v1'

export const buildSubcategoryFields = (
  isBookingContactEnabled: boolean,
  subcategory?: SubcategoryResponseModel
): {
  subcategoryFields: string[]
} => {
  const subcategoryFields = [...new Set(subcategory?.conditionalFields)]
  const isEvent = Boolean(subcategory?.isEvent)

  if (isEvent) {
    subcategoryFields.push('durationMinutes')
  }

  if (subcategory?.canBeDuo) {
    subcategoryFields.push('isDuo')
  }

  if (subcategory?.canBeWithdrawable) {
    subcategoryFields.push('withdrawalType')
    subcategoryFields.push('withdrawalDelay')
    if (isBookingContactEnabled) {
      subcategoryFields.push('bookingContact')
    }
  }

  return { subcategoryFields }
}
