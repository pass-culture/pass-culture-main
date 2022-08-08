import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import {
  DEFAULT_EAC_FORM_VALUES,
  IEducationalCategory,
  IEducationalSubCategory,
  IOfferEducationalFormValues,
} from 'core/OfferEducational'
import { SelectOption } from 'custom_types/form'
import FormLayout from 'new_components/FormLayout'
import { MultiSelectAutocomplete, Select, TextArea, TextInput } from 'ui-kit'

import {
  CATEGORY_LABEL,
  DESCRIPTION_LABEL,
  DURATION_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
} from '../../constants/labels'

interface IFormTypeProps {
  categories: IEducationalCategory[]
  subCategories: IEducationalSubCategory[]
  domainsOptions: SelectOption[]
  disableForm: boolean
}

const FormOfferType = ({
  categories,
  subCategories,
  domainsOptions,
  disableForm,
}: IFormTypeProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<IOfferEducationalFormValues>()
  const [availableSubCategories, setAvailableSubCategories] = useState<
    IEducationalSubCategory[] | null
  >(null)

  useEffect(() => {
    const subCategoryObject = subCategories.find(
      ({ id }) => id === values.subCategory
    )
    if (
      !values.subCategory ||
      (subCategoryObject && subCategoryObject.categoryId !== values.category)
    ) {
      setFieldValue('subCategory', DEFAULT_EAC_FORM_VALUES.subCategory, false)
    }

    setAvailableSubCategories(
      subCategories.filter(
        subCategory => subCategory.categoryId === values.category
      )
    )
  }, [values.category, setFieldValue, subCategories, values.subCategory])

  let categoriesOptions = categories.map(item => ({
    value: item['id'] as string,
    label: item['label'] as string,
  }))
  if (categoriesOptions.length > 1) {
    categoriesOptions = [
      { value: '', label: 'Sélectionner une catégorie' },
      ...categoriesOptions,
    ]
  }

  let subCategoriesOptions = availableSubCategories
    ? availableSubCategories.map(item => ({
        value: item['id'] as string,
        label: item['label'] as string,
      }))
    : []
  if (subCategoriesOptions.length > 1) {
    subCategoriesOptions = [
      { value: '', label: 'Sélectionner une sous catégorie' },
      ...subCategoriesOptions,
    ]
  }

  return (
    <FormLayout.Section
      description="Le type de l’offre permet de la caractériser et de la valoriser au mieux pour les enseignants et chefs d’établissement."
      title="Type d’offre"
    >
      <FormLayout.Row>
        <Select
          label={CATEGORY_LABEL}
          name="category"
          options={categoriesOptions}
          disabled={disableForm}
        />
      </FormLayout.Row>
      {!!availableSubCategories?.length && (
        <FormLayout.Row>
          <Select
            label={SUBCATEGORY_LABEL}
            name="subCategory"
            options={subCategoriesOptions}
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
      {domainsOptions.length > 0 && (
        <FormLayout.Row>
          <MultiSelectAutocomplete
            options={domainsOptions}
            pluralLabel="Domaines artistiques et culturels"
            label="Domaine artistique et culturel"
            fieldName="domains"
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
      <FormLayout.Row>
        <TextInput
          countCharacters
          label={TITLE_LABEL}
          maxLength={90}
          name="title"
          disabled={disableForm}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextArea
          countCharacters
          isOptional
          label={DESCRIPTION_LABEL}
          maxLength={1000}
          name="description"
          placeholder="Détaillez ici votre projet et son interêt pédagogique"
          disabled={disableForm}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          isOptional
          label={DURATION_LABEL}
          name="duration"
          placeholder="HH:MM"
          disabled={disableForm}
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormOfferType
