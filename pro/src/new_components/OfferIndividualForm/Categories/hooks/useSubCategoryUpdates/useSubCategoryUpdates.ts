import { useFormikContext } from 'formik'
import { useEffect } from 'react'

import { WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE } from 'core/Offers'
import { IOfferSubCategory } from 'core/Offers/types'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm/types'

import { SUBCATEGORIES_FIELDS_DEFAULT_VALUES } from '../../constants'

interface IUseSubCategoryUpdatesArgs {
  subCategories: IOfferSubCategory[]
}

const useSubCategoryUpdates = ({
  subCategories,
}: IUseSubCategoryUpdatesArgs) => {
  const {
    values: { subcategoryId },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  const resetSubCategoryFieldValues = (): void => {
    Object.entries(SUBCATEGORIES_FIELDS_DEFAULT_VALUES).forEach(
      ([field, value]: [string, string | undefined]) => {
        setFieldValue(field, value)
      }
    )
  }

  const setSubCategoryFields = (): void => {
    const subCategory = subCategories.find(
      (subcategory: IOfferSubCategory) => subcategoryId === subcategory.id
    )
    const subCategoryFields = subCategory?.conditionalFields || []
    const isEvent = subCategory?.isEvent || false

    isEvent && subCategoryFields.push('durationMinutes')
    subCategory?.canBeDuo && subCategoryFields.push('isDuo')

    WITHDRAWAL_TYPE_COMPATIBLE_SUBCATEGORIE.includes(subcategoryId) &&
      subCategoryFields.push('withdrawalType') &&
      subCategoryFields.push('withdrawalDelay')

    setFieldValue('subCategoryFields', subCategoryFields)
    setFieldValue('isEvent', isEvent)
  }

  useEffect(
    function onSubCategoryChange() {
      setSubCategoryFields()
      resetSubCategoryFieldValues()
    },
    [subcategoryId]
  )
}

export default useSubCategoryUpdates
