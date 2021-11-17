import React from 'react'

import { Category, SubCategory } from 'custom_types/categories'
import { OfferEducationalFormValues } from 'screens/OfferEducational/types'
import { Select, TextArea, TextInput } from 'ui-kit'

import {
  CATEGORY_LABEL,
  DESCRIPTION_LABEL,
  DURATION_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
} from '../../constants/labels'
import DurationPicker from '../DurationPicker'
import FormSection from '../FormSection'

import styles from './FormType.module.scss'
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
    <FormSection
      subtitle="Le type de l'offre permet de la caractériser et de la valoriser au mieux dans l'application."
      title="Type d'offre"
    >
      <div className={styles.subsection}>
        <Select
          label={CATEGORY_LABEL}
          name="category"
          options={buildOptions(categories)}
        />
      </div>
      <div className={styles.subsection}>
        <Select
          label={SUBCATEGORY_LABEL}
          name="subCategory"
          options={buildOptions(subCategoriesForSelectedCategory)}
        />
      </div>
      <div className={styles.subsection}>
        <TextInput label={TITLE_LABEL} name="title" />
      </div>
      <div className={styles.subsection}>
        <TextArea label={DESCRIPTION_LABEL} name="description" />
      </div>
      <div className={styles.subsection}>
        <DurationPicker
          label={DURATION_LABEL}
          name="duration"
          onChange={(value: number | null) => setFieldValue('duration', value)}
        />
      </div>
    </FormSection>
  )
}

export default EACOfferCreationType
