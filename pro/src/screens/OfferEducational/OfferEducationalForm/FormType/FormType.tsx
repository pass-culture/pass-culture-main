import React from 'react'

import { Category, SubCategory } from 'custom_types/categories'
import { Select, TextArea, TextInput } from 'ui-kit'

import FormSection from '../FormSection'

import styles from './FormType.module.scss'
import { buildOptions } from './utils/buildOptions'


interface IFormTypeProps {
    categories: Category[],
    subCategories: SubCategory[],
    values: Record<string, string>,
}

const EACOfferCreationType = ({
  categories,
  subCategories,
  values,
}: IFormTypeProps): JSX.Element => {
  const subCategoriesForSelectedCategory = subCategories.filter(subCategory => subCategory.categoryId === values.category)

  return (
    <FormSection
      subtitle="Le type de l'offre permet de la caractériser et de la valoriser au mieux dans l'application."
      title="Type d'offre"
    >
      <div className={styles.subsection}>
        <Select
          label="Domaine"
          name='category'
          options={buildOptions(categories)}
        />
      </div>
      <div className={styles.subsection}>
        <Select
          label="Sous Domaine"
          name='subCategory'
          options={buildOptions(subCategoriesForSelectedCategory)}
        />
      </div>
      <div className={styles.subsection}>
        <TextInput
          label="Titre de l'offre"
          name="title"
        />
      </div>
      <div className={styles.subsection}>
        <TextArea
          label="Description"
          name='description'
        />
      </div>
    </FormSection>
  )
}

export default EACOfferCreationType
