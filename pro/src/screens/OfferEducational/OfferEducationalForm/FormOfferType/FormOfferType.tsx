import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import {
  IEducationalCategory,
  IEducationalSubCategory,
  DEFAULT_EAC_FORM_VALUES,
  IOfferEducationalFormValues,
} from 'core/OfferEducational'
import FormLayout from 'new_components/FormLayout'
import { Select, TextArea, TextInput } from 'ui-kit'

import {
  CATEGORY_LABEL,
  DESCRIPTION_LABEL,
  DURATION_LABEL,
  SUBCATEGORY_LABEL,
  TITLE_LABEL,
} from '../../constants/labels'
import buildSelectOptions from '../../utils/buildSelectOptions'

interface IFormTypeProps {
  categories: IEducationalCategory[]
  subCategories: IEducationalSubCategory[]
}

const FormCategory = ({
  categories,
  subCategories,
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

  return (
    <FormLayout.Section
      description="Le type de l’offre permet de la caractériser et de la valoriser au mieux pour les enseignants et chefs d’établissement."
      title="Type d’offre"
    >
      <FormLayout.Row>
        <Select
          label={CATEGORY_LABEL}
          name="category"
          options={buildSelectOptions(
            categories,
            'label',
            'id',
            'Sélectionner une catégorie'
          )}
        />
      </FormLayout.Row>
      {!!availableSubCategories?.length && (
        <FormLayout.Row>
          <Select
            label={SUBCATEGORY_LABEL}
            name="subCategory"
            options={buildSelectOptions(
              availableSubCategories,
              'label',
              'id',
              'Sélectionner une sous catégorie'
            )}
          />
        </FormLayout.Row>
      )}
      <FormLayout.Row>
        <TextInput
          countCharacters
          label={TITLE_LABEL}
          maxLength={90}
          name="title"
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
        />
      </FormLayout.Row>
      <FormLayout.Row>
        <TextInput
          isOptional
          label={DURATION_LABEL}
          name="duration"
          placeholder="HH:MM"
        />
      </FormLayout.Row>
    </FormLayout.Section>
  )
}

export default FormCategory
