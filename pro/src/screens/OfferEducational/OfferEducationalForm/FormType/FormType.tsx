import React from 'react'

import { Category, SubCategory } from 'custom_types/categories'
import FormLayout from 'new_components/FormLayout'
import { Select, TextArea, TextInput } from 'ui-kit'

import {
  CATEGORY_LABEL,
  DESCRIPTION_LABEL,
  DURATION_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
} from '../../constants/labels'
import DurationPicker from '../DurationPicker'

import { buildOptions } from './utils/buildOptions'

interface IFormTypeProps {
  categories: Category[]
  subCategories: SubCategory[]
  values: OfferEducationalFormValues
  setFieldValue: (name: string, value: unknown) => void
}

const EACOfferCreationType = ({
  categories,
  subCategories,
  values,
  setFieldValue,
}: IFormTypeProps): JSX.Element => {
  const subCategoriesForSelectedCategory = subCategories.filter(
    subCategory => subCategory.categoryId === values.category
  )

  return (
    <FormLayout.Section
      description="Le type de l'offre permet de la caractériser et de la valoriser au mieux dans l'application."
      title="Type d'offre"
    >
      <FormLayout.Row>
        <Select
          label={CATEGORY_LABEL}
          name="category"
          options={buildOptions(categories)}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <Select
          label={SUBCATEGORY_LABEL}
          name="subCategory"
          options={buildOptions(subCategoriesForSelectedCategory)}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput label={TITLE_LABEL} name="title" />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextArea label={DESCRIPTION_LABEL} name="description" />
      </FormLayout.Row>
      <FormLayout.Row>
        <DurationPicker
          label={DURATION_LABEL}
          name="duration"
          onChange={(value: number | null) => setFieldValue('duration', value)}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default EACOfferCreationType
