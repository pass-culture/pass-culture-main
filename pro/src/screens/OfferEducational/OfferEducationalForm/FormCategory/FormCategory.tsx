import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'

import {
  IEducationalCategory,
  IEducationalSubCategory,
  INITIAL_EDUCATIONAL_FORM_VALUES,
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
import DurationPicker from '../DurationPicker'

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
    setFieldValue(
      'subCategory',
      INITIAL_EDUCATIONAL_FORM_VALUES.subCategory,
      false
    )

    setAvailableSubCategories(
      subCategories.filter(
        subCategory => subCategory.categoryId === values.category
      )
    )
  }, [values.category, setFieldValue, subCategories])

  return (
    <FormLayout.Section
      description="Le type de l'offre permet de la caractériser et de la valoriser au mieux dans l'application."
      title="Type d'offre"
    >
      <FormLayout.Row>
        <Select
          label={CATEGORY_LABEL}
          name="category"
          options={buildSelectOptions(
            categories,
            'label',
            'id',
            'Selectionner une catégorie'
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
              'Selectionner une sous catégorie'
            )}
          />
        </FormLayout.Row>
      )}
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

export default FormCategory
