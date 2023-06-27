import { OfferSubCategory } from 'core/Offers/types'

const buildSubCategoryFields = (
  subCategoryId: string,
  subCategories: OfferSubCategory[]
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

  return { subCategoryFields, isEvent }
}

export default buildSubCategoryFields
