import { useFormikContext } from 'formik'
import { useEffect } from 'react'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm/types'
import { setSubCategoryFields } from 'components/OfferIndividualForm/utils'
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

  const resetSubCategoryFieldValues = (): void => {
    Object.entries(SUBCATEGORIES_FIELDS_DEFAULT_VALUES).forEach(
      ([field, value]: [string, string | undefined]) => {
        setFieldValue(field, value)
      }
    )
  }

  const setFormSubCategoryFields = (): void => {
    const { subCategoryFields, isEvent } = setSubCategoryFields(
      subcategoryId,
      subCategories
    )
    setFieldValue('subCategoryFields', subCategoryFields)
    setFieldValue('isEvent', isEvent)
    setFieldValue(
      'isDuo',
      !!subCategories.find(s => s.id == subcategoryId)?.canBeDuo
    )
  }

  useEffect(
    function onSubCategoryChange() {
      if (dirty) {
        const previousSubCategoryFields = subCategoryFields
        setFormSubCategoryFields()

        if (previousSubCategoryFields !== subCategoryFields) {
          resetSubCategoryFieldValues()
        }
      }
    },
    [subcategoryId]
  )
}

export default useSubCategoryUpdates
