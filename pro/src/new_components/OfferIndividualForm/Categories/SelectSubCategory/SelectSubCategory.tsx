import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import { IOfferSubCategory } from 'core/Offers/types'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'

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
      const subCategory = subCategories.find(
        (subcategory: IOfferSubCategory) => subcategoryId === subcategory.id
      )
      const subCategoryFields = subCategory?.conditionalFields || []
      const isEvent = subCategory?.isEvent || false
      setFieldValue('subCategoryFields', subCategoryFields)
      setFieldValue('isEvent', isEvent)
    },
    [subcategoryId]
  )

  const options: SelectOptions = subCategories
    .filter((s: IOfferSubCategory) => s.categoryId === categoryId)
    .map((s: IOfferSubCategory) => ({
      value: s.id,
      label: s.proLabel,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))

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
