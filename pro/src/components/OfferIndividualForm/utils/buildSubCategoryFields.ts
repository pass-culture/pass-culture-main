import { WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE } from 'core/Offers'
import { IOfferSubCategory } from 'core/Offers/types'

const buildSubCategoryFields = (
  subCategoryId: string,
  subCategories: IOfferSubCategory[]
): {
  subCategoryFields: string[]
  isEvent: boolean
} => {
  const subCategory = subCategories.find(
    (subcategory: IOfferSubCategory) => subCategoryId === subcategory.id
  )
  let subCategoryFields: string[] = [...(subCategory?.conditionalFields || [])]
  if (subCategoryFields.includes('showType')) {
    subCategoryFields.push('showSubType')
  }
  if (subCategoryFields.includes('musicType')) {
    subCategoryFields.push('musicSubType')
  }
  subCategoryFields = [...new Set(subCategoryFields)]
  const isEvent = subCategory?.isEvent || false

  isEvent && subCategoryFields.push('durationMinutes')
  subCategory?.canBeDuo && subCategoryFields.push('isDuo')

  WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(subCategoryId) &&
    subCategoryFields.push('withdrawalType') &&
    subCategoryFields.push('withdrawalDelay')

  return { subCategoryFields, isEvent }
}

export default buildSubCategoryFields
