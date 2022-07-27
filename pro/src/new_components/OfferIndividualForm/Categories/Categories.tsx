import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import FormLayout from 'new_components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'

import { MusicTypes } from './MusicTypes'
import { SelectSubCategory } from './SelectSubCategory'
import { ShowTypes } from './ShowTypes'

export interface ICategoriesProps {
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
}

const Categories = ({
  categories,
  subCategories,
}: ICategoriesProps): JSX.Element => {
  const { values: formValues, setFieldValue } =
    useFormikContext<IOfferIndividualFormValues>()
  useEffect(() => {
    setFieldValue('subcategoryId', FORM_DEFAULT_VALUES.subcategoryId)
  }, [formValues.categoryId])

  const categoryOptions: SelectOptions = categories
    .map((c: IOfferCategory) => ({
      value: c.id,
      label: c.proLabel,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))

  const hasSubCategory =
    formValues.categoryId !== FORM_DEFAULT_VALUES.categoryId
  const hasMusicType = formValues.subCategoryFields.includes('musicType')
  const hasShowType = formValues.subCategoryFields.includes('showType')

  return (
    <FormLayout.Section
      title="Type d’offre"
      description="Le type de l’offre permet de la caractériser et de la valoriser au mieux dans l’application."
    >
      <FormLayout.Row smSpaceAfter={true}>
        <Select
          label="Choisir une catégorie"
          name="categoryId"
          options={categoryOptions}
          defaultOption={{
            label: 'Choisir une catégorie',
            value: FORM_DEFAULT_VALUES.categoryId,
          }}
        />
      </FormLayout.Row>

      {hasSubCategory && (
        <FormLayout.Row>
          <SelectSubCategory subCategories={subCategories} />
        </FormLayout.Row>
      )}

      {hasMusicType && (
        <FormLayout.Row>
          <MusicTypes />
        </FormLayout.Row>
      )}

      {hasShowType && (
        <FormLayout.Row>
          <ShowTypes />
        </FormLayout.Row>
      )}
    </FormLayout.Section>
  )
}

export default Categories
