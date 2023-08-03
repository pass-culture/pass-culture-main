import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import FormLayout from 'components/FormLayout'
import {
  DEFAULT_EAC_FORM_VALUES,
  EducationalCategory,
  EducationalSubCategory,
  OfferEducationalFormValues,
  MAX_DETAILS_LENGTH,
} from 'core/OfferEducational'
import { SelectOption } from 'custom_types/form'
import {
  InfoBox,
  MultiSelectAutocomplete,
  Select,
  TextArea,
  TextInput,
} from 'ui-kit'

import {
  CATEGORY_LABEL,
  DESCRIPTION_LABEL,
  DURATION_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
} from '../../constants/labels'

interface FormTypeProps {
  categories: EducationalCategory[]
  subCategories: EducationalSubCategory[]
  domainsOptions: SelectOption[]
  nationalPrograms: SelectOption[]
  disableForm: boolean
}

const FormOfferType = ({
  categories,
  subCategories,
  domainsOptions,
  nationalPrograms,
  disableForm,
}: FormTypeProps): JSX.Element => {
  const { values, setFieldValue } =
    useFormikContext<OfferEducationalFormValues>()
  const [availableSubCategories, setAvailableSubCategories] = useState<
    EducationalSubCategory[] | null
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
            name="domains"
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
      {nationalPrograms.length > 0 && (
        <FormLayout.Row
          sideComponent={
            <InfoBox>
              Un dispositif national est un type de programme d’éducation
              artistique et culturelle auquel sont rattachées certaines offres.
              Si c’est le cas de cette offre, merci de le renseigner.
            </InfoBox>
          }
        >
          <Select
            options={[
              {
                label: 'Sélectionnez un dispositif national',
                value: '',
              },
              ...nationalPrograms,
            ]}
            label="Dispositif national"
            name="nationalProgramId"
            placeholder="Séléctionner un dispositif national"
            isOptional
            disabled={disableForm}
          />
        </FormLayout.Row>
      )}
      <FormLayout.Row>
        <TextInput
          countCharacters
          label={TITLE_LABEL}
          maxLength={110}
          name="title"
          disabled={disableForm}
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextArea
          countCharacters
          label={DESCRIPTION_LABEL}
          maxLength={MAX_DETAILS_LENGTH}
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
