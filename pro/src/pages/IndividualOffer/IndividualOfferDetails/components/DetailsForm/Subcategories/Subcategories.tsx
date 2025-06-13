import { useFormContext } from 'react-hook-form'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  onSubcategoryChange,
  onCategoryChange,
  buildCategoryOptions,
  buildSubcategoryOptions,
} from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Select } from 'ui-kit/formV2/Select/Select'

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
    watch,
    register,
    setValue,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const categoryId = watch('categoryId')

  const subcategoryConditionalFields = watch('subcategoryConditionalFields')

  const categoryOptions = buildCategoryOptions(filteredCategories)
  const subcategoryOptions = buildSubcategoryOptions(
    filteredSubcategories,
    categoryId
  )

  return (
    <FormLayout.Section
      title={'Type d’offre'}
      className={styles['subcategories-section']}
    >
      <FormLayout.Row>
        <Select
          label="Catégorie"
          required
          options={categoryOptions}
          defaultOption={{
            label: 'Choisir une catégorie',
            value: DEFAULT_DETAILS_FORM_VALUES.categoryId,
          }}
          disabled={readOnlyFields.includes('categoryId')}
          {...register('categoryId')}
          onChange={(event: React.ChangeEvent<HTMLSelectElement>) => {
            onCategoryChange({
              categoryId: event.target.value,
              readOnlyFields,
              subcategories: filteredSubcategories,
              setFieldValue: setValue,
              onSubcategoryChange,
              subcategoryConditionalFields,
            })
            setValue('categoryId', event.target.value)
          }}
          error={errors.categoryId?.message}
        />
      </FormLayout.Row>
      {categoryId !== DEFAULT_DETAILS_FORM_VALUES.categoryId && (
        <Select
          label="Sous-catégorie"
          className={styles['subcategory-select']}
          required
          options={subcategoryOptions}
          defaultOption={{
            label: 'Choisir une sous-catégorie',
            value: DEFAULT_DETAILS_FORM_VALUES.subcategoryId,
          }}
          name="subcategoryId"
          onChange={(event: React.ChangeEvent<HTMLSelectElement>) => {
            onSubcategoryChange({
              newSubCategoryId: event.target.value,
              subcategories: filteredSubcategories,
              setFieldValue: setValue,
              subcategoryConditionalFields,
            })
            setValue('subcategoryId', event.target.value)
          }}
          value={watch('subcategoryId')}
          error={errors.subcategoryId?.message}
          disabled={
            readOnlyFields.includes('subcategoryId') ||
            subcategoryOptions.length === 1
          }
        />
      )}
    </FormLayout.Section>
  )
}
