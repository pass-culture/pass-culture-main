import type { ChangeEvent } from 'react'
import { useFormContext } from 'react-hook-form'

import type {
  CategoryResponseModel,
  SubcategoryResponseModel,
} from '@/apiClient/v1'
import { useIndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import { FormLayout } from '@/components/FormLayout/FormLayout'
import { Banner } from '@/design-system/Banner/Banner'
import { DEFAULT_DETAILS_FORM_VALUES } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import {
  buildCategoryOptions,
  buildSubcategoryOptions,
  completeSubcategoryConditionalFields,
} from '@/pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Select } from '@/ui-kit/form/Select/Select'

import { ARTISTIC_INFORMATION_FIELDS } from '../DetailsSubForm/DetailsSubForm'
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
    resetField,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()
  const { setIsEvent } = useIndividualOfferContext()

  const categoryId = watch('categoryId')
  const subcategoryId = watch('subcategoryId')

  const categoryOptions = buildCategoryOptions(filteredCategories)
  const subcategoryOptions = buildSubcategoryOptions(
    filteredSubcategories,
    categoryId
  )

  const handleSubcategoryUpdate = (nextSubcategoryId: string) => {
    const nextSubcategory = filteredSubcategories.find(
      (s) => s.id === nextSubcategoryId
    )
    if (!nextSubcategory) {
      throw new Error(
        `nextSubcategory with id '${subcategoryId}' not found in filteredSubcategories.`
      )
    }
    const newConditionalFields =
      completeSubcategoryConditionalFields(nextSubcategory)

    ARTISTIC_INFORMATION_FIELDS.forEach((field) => {
      resetField(field)
    })
    setValue('subcategoryConditionalFields', newConditionalFields, {
      shouldValidate: true,
    })

    setIsEvent(nextSubcategory.isEvent)
  }

  const handleCategoryChange = (event: ChangeEvent<HTMLSelectElement>) => {
    clearErrors(['categoryId', 'subcategoryId'])

    const nextCategoryId = event.target.value
    if (nextCategoryId === DEFAULT_DETAILS_FORM_VALUES.categoryId) {
      resetField('subcategoryId')
      setValue(
        'subcategoryConditionalFields',
        DEFAULT_DETAILS_FORM_VALUES.subcategoryConditionalFields
      )

      return
    }

    const options = buildSubcategoryOptions(
      filteredSubcategories,
      nextCategoryId
    )
    if (options.length > 1) {
      resetField('subcategoryId')

      return
    }

    const nextSubcategoryId = options[0].value

    setValue('subcategoryId', nextSubcategoryId, {
      shouldValidate: true,
    })
    handleSubcategoryUpdate(nextSubcategoryId)
  }

  const handleSubcategoryChange = (event: ChangeEvent<HTMLSelectElement>) => {
    const nextSubcategoryId = event.target.value
    if (nextSubcategoryId === DEFAULT_DETAILS_FORM_VALUES.subcategoryId) {
      setValue(
        'subcategoryConditionalFields',
        DEFAULT_DETAILS_FORM_VALUES.subcategoryConditionalFields
      )

      return
    }

    handleSubcategoryUpdate(nextSubcategoryId)
  }

  return (
    <FormLayout.Section
      title="Type d’offre"
      className={styles['subcategories-section']}
    >
      <FormLayout.Row>
        <Select
          {...register('categoryId', {
            onChange: handleCategoryChange,
          })}
          label="Catégorie"
          required
          options={categoryOptions}
          defaultOption={{
            label: 'Choisir une catégorie',
            value: DEFAULT_DETAILS_FORM_VALUES.categoryId,
          }}
          value={categoryId}
          disabled={readOnlyFields.includes('categoryId')}
          error={errors.categoryId?.message}
        />
      </FormLayout.Row>

      {categoryId !== DEFAULT_DETAILS_FORM_VALUES.categoryId && (
        <>
          <Select
            {...register('subcategoryId', {
              onChange: handleSubcategoryChange,
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
            error={errors.subcategoryId?.message}
          />
          {!readOnlyFields.includes('categoryId') && (
            <div className={styles['subcategory-callout']}>
              <Banner
                title="Étapes adaptatives"
                description="Le formulaire s'adaptera automatiquement selon la sous-catégorie sélectionnée."
              />
            </div>
          )}
        </>
      )}
    </FormLayout.Section>
  )
}
