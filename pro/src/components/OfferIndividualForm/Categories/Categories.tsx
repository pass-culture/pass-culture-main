import { useFormikContext } from 'formik'
import React, { useEffect } from 'react'

import FormLayout from 'components/FormLayout'
import {
  FORM_DEFAULT_VALUES,
  IOfferIndividualFormValues,
} from 'components/OfferIndividualForm'
import { IOfferCategory, IOfferSubCategory } from 'core/Offers/types'
import { InfoBox, Select } from 'ui-kit'

import styles from '../OfferIndividualForm.module.scss'

import { MusicTypes } from './MusicTypes'
import { SelectSubCategory } from './SelectSubCategory'
import { ShowTypes } from './ShowTypes'

export interface ICategoriesProps {
  categories: IOfferCategory[]
  subCategories: IOfferSubCategory[]
  readOnlyFields?: string[]
  Banner?: React.ReactNode
}

const Categories = ({
  categories,
  subCategories,
  readOnlyFields = [],
  Banner,
}: ICategoriesProps): JSX.Element => {
  const {
    values: formValues,
    setFieldValue,
    setFieldTouched,
  } = useFormikContext<IOfferIndividualFormValues>()
  useEffect(() => {
    const currentSubcategories = subCategories.filter(
      e => e.categoryId === formValues.categoryId
    )
    const containsSubcategory = currentSubcategories.some(
      e => e.id === formValues.subcategoryId
    )
    if (
      formValues.subcategoryId === '' ||
      formValues.categoryId === '' ||
      (currentSubcategories.length > 1 && !containsSubcategory)
    ) {
      setFieldValue('subcategoryId', FORM_DEFAULT_VALUES.subcategoryId)
      setFieldValue('subCategoryFields', FORM_DEFAULT_VALUES.subCategoryFields)
      setFieldTouched('subcategoryId', false)
    }
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
    <FormLayout.Section title="Type d’offre">
      <FormLayout.Row
        className={
          hasSubCategory || !!Banner ? undefined : styles['category-row']
        }
        sideComponent={
          <InfoBox
            type="info"
            text="Une sélection précise de vos catégories permettra au grand public de facilement trouver votre offre. Une fois validées, vous ne pourrez pas les modifier."
            link={{
              isExternal: true,
              to: 'https://aide.passculture.app/hc/fr/articles/4411999013265--Acteurs-Culturels-Quelle-cat%C3%A9gorie-et-sous-cat%C3%A9gorie-choisir-lors-de-la-cr%C3%A9ation-d-offres-',
              text: 'Quelles catégories choisir ?',
              target: '_blank',
              rel: 'noopener noreferrer',
            }}
          />
        }
      >
        <Select
          label="Catégorie"
          name="categoryId"
          options={categoryOptions}
          defaultOption={{
            label: 'Choisir une catégorie',
            value: FORM_DEFAULT_VALUES.categoryId,
          }}
          disabled={readOnlyFields.includes('categoryId')}
        />
      </FormLayout.Row>

      {hasSubCategory && (
        <FormLayout.Row>
          <SelectSubCategory
            subCategories={subCategories}
            readOnly={readOnlyFields.includes('subcategoryId')}
          />
        </FormLayout.Row>
      )}

      {hasMusicType && (
        <MusicTypes readOnly={readOnlyFields.includes('musicType')} />
      )}

      {hasShowType && (
        <ShowTypes readOnly={readOnlyFields.includes('showType')} />
      )}
      {!!Banner && <FormLayout.Row>{Banner}</FormLayout.Row>}
    </FormLayout.Section>
  )
}

export default Categories
