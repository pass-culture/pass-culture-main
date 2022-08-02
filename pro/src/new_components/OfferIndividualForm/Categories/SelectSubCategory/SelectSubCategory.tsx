import { useFormikContext } from 'formik'
import React from 'react'

import { IOfferSubCategory } from 'core/Offers/types'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'

import useSubCategoryUpdates from '../hooks/useSubCategoryUpdates/useSubCategoryUpdates'

interface ISelectSubCategoryProps {
  subCategories: IOfferSubCategory[]
}

const SelectSubCategory = ({
  subCategories,
}: ISelectSubCategoryProps): JSX.Element => {
  const {
    values: { categoryId },
  } = useFormikContext<IOfferIndividualFormValues>()

  useSubCategoryUpdates({ subCategories })

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
