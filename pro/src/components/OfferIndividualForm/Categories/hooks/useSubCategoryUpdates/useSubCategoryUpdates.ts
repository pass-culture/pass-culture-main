import { useFormikContext } from 'formik'
import { useEffect } from 'react'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm/types'
import { buildSubCategoryFields } from 'components/OfferIndividualForm/utils'
import { IOfferSubCategory } from 'core/Offers/types'

import { SUBCATEGORIES_FIELDS_DEFAULT_VALUES } from '../../constants'

interface IUseSubCategoryUpdatesArgs {
  subCategories: IOfferSubCategory[]
}

const useSubCategoryUpdates = ({
  subCategories,
}: IUseSubCategoryUpdatesArgs) => {
  const {
    dirty,
    values: { subcategoryId, subCategoryFields },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  const resetSubCategoryFieldValues = (fieldsToReset: string[]): void => {
    fieldsToReset.forEach((field: string) => {
      if (field in SUBCATEGORIES_FIELDS_DEFAULT_VALUES) {
        setFieldValue(
          field,
          SUBCATEGORIES_FIELDS_DEFAULT_VALUES[
            field as keyof typeof SUBCATEGORIES_FIELDS_DEFAULT_VALUES
          ]
        )
      }
    })
  }

  const setSubCategoryFields = (): string[] => {
    const { subCategoryFields, isEvent } = buildSubCategoryFields(
      subcategoryId,
      subCategories
    )
    setFieldValue('subCategoryFields', subCategoryFields)
    setFieldValue('isEvent', isEvent)
    setFieldValue(
      'isDuo',
      !!subCategories.find(s => s.id == subcategoryId)?.canBeDuo
    )
    return subCategoryFields
  }

  useEffect(
    function onSubCategoryChange() {
      if (dirty) {
        const newSubCategoryFields = setSubCategoryFields()
        if (newSubCategoryFields !== subCategoryFields) {
          resetSubCategoryFieldValues(
            subCategoryFields.filter(
              (field: string) => !newSubCategoryFields.includes(field)
            )
          )
        }
      }
    },
    [subcategoryId]
  )
}

export default useSubCategoryUpdates
