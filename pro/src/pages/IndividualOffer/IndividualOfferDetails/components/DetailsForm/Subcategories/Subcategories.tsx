import { useFormContext } from 'react-hook-form'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  buildCategoryOptions,
  buildSubcategoryOptions,
  completeSubcategoryConditionalFields,
} from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Select } from 'ui-kit/form/Select/Select'

import styles from './Subcategories.module.scss'

type SubcategoriesProps = {
  readOnlyFields: string[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
}

export function Subcategories({
  readOnlyFields,
  filteredCategories,
  filteredSubcategories,
}: SubcategoriesProps) {
  const {
    setValue,
    clearErrors,
    watch,
    register,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const categoryId = watch('categoryId')
  const subcategoryId = watch('subcategoryId')

  const categoryOptions = buildCategoryOptions(filteredCategories)
  const subcategoryOptions = buildSubcategoryOptions(
    filteredSubcategories,
    categoryId
  )

  const handleSubcategoryChange = (subcategoryId: string) => {
    const subcategory = filteredSubcategories.find(
      (s) => s.id === subcategoryId
    )
    const newConditionalFields =
      completeSubcategoryConditionalFields(subcategory)

    setValue('subcategoryId', subcategoryId, {
      shouldValidate: true,
    })
    setValue('subcategoryConditionalFields', newConditionalFields, {
      shouldValidate: true,
    })
  }

  const handleCategoryChange = (categoryId: string) => {
    clearErrors(['categoryId', 'subcategoryId'])
    setValue('categoryId', categoryId, {
      shouldValidate: true,
    })

    if (readOnlyFields.includes('subcategoryId')) {
      return
    }

    const options = buildSubcategoryOptions(filteredSubcategories, categoryId)
    const nextSubcategoryId =
      options.length === 1
        ? String(options[0].value)
        : DEFAULT_DETAILS_FORM_VALUES.subcategoryId

    handleSubcategoryChange(nextSubcategoryId)
  }

  return (
    <FormLayout.Section
      title="Type d’offre"
      className={styles['subcategories-section']}
    >
      <FormLayout.Row>
        <Select
          {...register('categoryId')}
          label="Catégorie"
          required
          options={categoryOptions}
          defaultOption={{
            label: 'Choisir une catégorie',
            value: DEFAULT_DETAILS_FORM_VALUES.categoryId,
          }}
          value={categoryId}
          disabled={readOnlyFields.includes('categoryId')}
          onChange={(event) => {
            handleCategoryChange(event.target.value)
            clearErrors(['categoryId', 'subcategoryId'])
          }}
          error={errors.categoryId?.message}
        />
      </FormLayout.Row>

      {categoryId !== DEFAULT_DETAILS_FORM_VALUES.categoryId && (
        <Select
          {...register('subcategoryId', {
            required: 'Veuillez sélectionner une sous-catégorie',
          })}
          label="Sous-catégorie"
          className={styles['subcategory-select']}
          required
          options={subcategoryOptions}
          defaultOption={{
            label: 'Choisir une sous-catégorie',
            value: DEFAULT_DETAILS_FORM_VALUES.subcategoryId,
          }}
          value={subcategoryId}
          disabled={
            readOnlyFields.includes('subcategoryId') ||
            subcategoryOptions.length === 1
          }
          onChange={(event) => {
            handleSubcategoryChange(event.target.value)
            clearErrors(['subcategoryId'])
          }}
          error={errors.subcategoryId?.message}
        />
      )}
    </FormLayout.Section>
  )
}
