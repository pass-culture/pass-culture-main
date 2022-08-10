import { WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE } from 'core/Offers'
import { IOfferSubCategory } from 'core/Offers/types'

const setSubCategoryFields = (
  subCategoryId: string,
  subCategories: IOfferSubCategory[]
): {
  subCategoryFields: string[]
  isEvent: boolean
} => {
  const subCategory = subCategories.find(
    (subcategory: IOfferSubCategory) => subCategoryId === subcategory.id
  )
  const subCategoryFields = subCategory?.conditionalFields || []
  const isEvent = subCategory?.isEvent || false

  isEvent && subCategoryFields.push('durationMinutes')
  subCategory?.canBeDuo && subCategoryFields.push('isDuo')

  WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(subCategoryId) &&
    subCategoryFields.push('withdrawalType') &&
    subCategoryFields.push('withdrawalDelay')

  return { subCategoryFields, isEvent }
}

export default setSubCategoryFields
