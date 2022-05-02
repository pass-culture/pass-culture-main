import React, { useCallback, useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { useFormikContext } from 'formik'

import { CATEGORY_STATUS } from 'core/Offers'
import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'
import { FORM_DEFAULT_VALUES } from 'new_components/OfferIndividualForm'
import { Select } from 'ui-kit'


import { MusicTypes } from './MusicTypes'
import { ShowTypes } from './ShowTypes'
import { Category, SubCategory } from 'custom_types/categories'
import { buildSelectOptions } from './utils'

interface ICategoriesProps {
  categories: Category[]
  subcategories: SubCategory[]
}

interface IOption {
  value: string
  label: string
}

const Categories = ({
  categories,
  subcategories,
}: ICategoriesProps ): JSX.Element => {
  const { values: { categoryId, subcategoryId } } = useFormikContext<IOfferIndividualFormValues>()
  const location = useLocation()
  const queryParams = new URLSearchParams(location.search)
  const [subcategoriesOptions, setSubcategoriesOptions] = useState<IOption[]>(
    []
  )
  const [subcategoryConditionalFields, setSubcategoryConditionalFields] =
    useState<string[] | undefined>([])

  const categoryIsVirtual = useCallback(
    (categoryId: string) => {
      return (
        subcategories.filter(
          (s: SubCategory) =>
            s.categoryId === categoryId &&
            [
              CATEGORY_STATUS.ONLINE,
              CATEGORY_STATUS.ONLINE_OR_OFFLINE,
            ].includes(s.onlineOfflinePlatform)
        ).length > 0
      )
    },
    [subcategories]
  )

  const categoryFilters = useCallback(
    (category: Category) => {
      return (
        category.isSelectable &&
        categoryIsVirtual(category.id)
      )
    },
    [categoryIsVirtual]
  )

  let categoriesOptions: IOption[] = []
  if (categories) {
    categoriesOptions = buildSelectOptions<Category>(
      c => c.id,
      c => c.proLabel,
      categories.filter(categoryFilters)
    )
  }

  useEffect(
    function onCategoryChange() {
      if (categoryId !== FORM_DEFAULT_VALUES.categoryId) {
        let options = subcategories.filter(
          (subcategory: SubCategory) =>
            subcategory.categoryId === categoryId &&
            subcategory.isSelectable
        )
        setSubcategoriesOptions(buildSelectOptions<SubCategory>(c => c.id, c => c.proLabel, options))
      } else {
        setSubcategoriesOptions([])
      }
    },
    [categoryId, subcategories]
  )

  useEffect(
    function onSubcategoryChange() {
      if (subcategoryId !== FORM_DEFAULT_VALUES.subcategoryId) {
        const currentSubCategoryConditionalFields = subcategories
          .find(
            (subcategory: SubCategory) =>
              subcategoryId === subcategory.id
          )
          ?.conditionalFields.filter(
            (field: string) => field === 'musicType' || field === 'showType'
          )
        setSubcategoryConditionalFields(currentSubCategoryConditionalFields)
      } else {
        setSubcategoryConditionalFields([])
      }
    },
    [subcategoryId, subcategories]
  )

  return (
    <FormLayout.Section
      title='Type d’offre'
      description='Le type de l’offre permet de la caractériser et de la valoriser au mieux dans l’application.'
    >
      <Select
        label='Choisir une catégorie'
        name='categoryId'
        options={categoriesOptions}
        defaultOption={{
          label: 'Choisir une catégorie',
          value: FORM_DEFAULT_VALUES.categoryId,
        }}
      />

      {subcategoriesOptions.length > 0 && (
        <>
          <Select
            label='Choisir une sous-catégorie'
            name='subcategoryId'
            options={subcategoriesOptions}
            defaultOption={{
              label: 'Choisir une sous-catégorie',
              value: FORM_DEFAULT_VALUES.subcategoryId,
            }}
          />

          {subcategoryConditionalFields && subcategoryConditionalFields.length > 0 && (
            <>
            {subcategoryConditionalFields.includes('musicType') && (
              <MusicTypes />
            )}
            {subcategoryConditionalFields.includes('showType') && (
              <ShowTypes />
            )}
            </>
          )}
        </>
      )}
    </FormLayout.Section>
  )
}

export default Categories
