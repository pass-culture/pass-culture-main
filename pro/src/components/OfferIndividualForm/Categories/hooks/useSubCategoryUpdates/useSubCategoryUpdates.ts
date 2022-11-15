import { useFormikContext } from 'formik'
import { useEffect } from 'react'

import { IOfferIndividualFormValues } from 'components/OfferIndividualForm/types'
import { setSubCategoryFields } from 'components/OfferIndividualForm/utils'
import { IOfferSubCategory } from 'core/Offers/types'

interface IUseSubCategoryUpdatesArgs {
  subCategories: IOfferSubCategory[]
}

const useSubCategoryUpdates = ({
  subCategories,
}: IUseSubCategoryUpdatesArgs) => {
  const {
    dirty,
    values: { subcategoryId },
    setFieldValue,
    setTouched,
  } = useFormikContext<IOfferIndividualFormValues>()
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
        setFormSubCategoryFields()
        if (subcategoryId !== '') {
          setTouched({
            categoryId: true,
            subcategoryId: true,
          })
        }
      }
    },
    [subcategoryId]
  )
}

export default useSubCategoryUpdates
