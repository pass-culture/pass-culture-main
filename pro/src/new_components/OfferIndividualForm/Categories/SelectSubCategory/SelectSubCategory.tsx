import React, { useEffect } from 'react'

import { FORM_DEFAULT_VALUES } from 'new_components/OfferIndividualForm'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'
import { IOfferSubCategory } from 'core/Offers/types'
import { Select } from 'ui-kit'
import { useFormikContext } from 'formik'

interface ISelectSubCategoryProps {
  subCategories: IOfferSubCategory[]
}

const SelectSubCategory = ({
  subCategories,
}: ISelectSubCategoryProps): JSX.Element => {
  const {
    values: { categoryId, subcategoryId },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  useEffect(
    function onSubCategoryChange() {
      const subCategoryFields =
        subCategories.find(
          (subcategory: IOfferSubCategory) => subcategoryId === subcategory.id
        )?.conditionalFields || []
      setFieldValue('subCategoryFields', subCategoryFields)
    },
    [subcategoryId]
  )

  const options: SelectOptions = subCategories
    .filter((s: IOfferSubCategory) => s.categoryId === categoryId)
    .map((s: IOfferSubCategory) => ({
      value: s.id,
      label: s.proLabel,
    }))

  return (
    <Select
      label="Choisir une sous-catégorie"
      name="subcategoryId"
      options={options}
      defaultOption={{
        label: 'Choisir une sous-catégorie',
        value: FORM_DEFAULT_VALUES.subcategoryId,
      }}
    />
  )
}

export default SelectSubCategory
