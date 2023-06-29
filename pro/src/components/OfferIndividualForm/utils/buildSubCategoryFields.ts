import { OfferSubCategory } from 'core/Offers/types'

const buildSubCategoryFields = (
  subCategoryId: string,
  subCategories: OfferSubCategory[],
  isBookingContactEnabled: boolean
): {
  subCategoryFields: string[]
  isEvent: boolean
} => {
  const subCategory = subCategories.find(
    (subcategory: OfferSubCategory) => subCategoryId === subcategory.id
  )
  const subCategoryFields = [...new Set(subCategory?.conditionalFields || [])]
  const isEvent = subCategory?.isEvent || false

  isEvent && subCategoryFields.push('durationMinutes')
  subCategory?.canBeDuo && subCategoryFields.push('isDuo')

  subCategory?.canBeWithdrawable &&
    subCategoryFields.push('withdrawalType') &&
    subCategoryFields.push('withdrawalDelay')

  isBookingContactEnabled &&
    subCategory?.canBeWithdrawable &&
    subCategoryFields.push('bookingContact')

  return { subCategoryFields, isEvent }
}

export default buildSubCategoryFields
