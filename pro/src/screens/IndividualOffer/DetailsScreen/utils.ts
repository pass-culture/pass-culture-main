import { FormikErrors } from 'formik'

import {
  CategoryResponseModel,
  SubcategoryResponseModel,
  VenueListItemResponseModel,
} from 'apiClient/v1'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { SelectOption } from 'custom_types/form'
import { computeVenueDisplayName } from 'repository/venuesService'

import { DEFAULT_DETAILS_INTITIAL_VALUES } from './constants'
import { DetailsFormValues } from './types'

export const buildCategoryOptions = (
  categories: CategoryResponseModel[]
): SelectOption[] =>
  categories
    .filter((category: CategoryResponseModel) => category.isSelectable)
    .map((category: CategoryResponseModel) => ({
      value: category.id,
      label: category.proLabel,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))

export const buildSubcategoryOptions = (
  subCategories: SubcategoryResponseModel[],
  categoryId: string
): SelectOption[] =>
  buildCategoryOptions(
    subCategories.filter(
      (subCategory: SubcategoryResponseModel) =>
        subCategory.categoryId === categoryId
    )
  )

export const buildShowSubTypeOptions = (showType: string): SelectOption[] => {
  if (showType === DEFAULT_DETAILS_INTITIAL_VALUES.showType) {
    return []
  }

  const selectedShowTypeChildren = showOptionsTree.find(
    (showTypeOption) => showTypeOption.code === parseInt(showType)
  )?.children

  if (!selectedShowTypeChildren) {
    return []
  }

  return selectedShowTypeChildren
    .map((data) => ({
      value: data.code.toString(),
      label: data.label,
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
}

export const buildSubcategoryConditonalFields = (
  subcategory?: SubcategoryResponseModel
): {
  subcategoryConditionalFields: string[]
} => {
  const subcategoryConditionalFields = [
    ...new Set(subcategory?.conditionalFields),
  ]
  const isEvent = Boolean(subcategory?.isEvent)

  if (isEvent) {
    subcategoryConditionalFields.push('durationMinutes')
  }

  return { subcategoryConditionalFields }
}

type OnSubcategoryChangeProps = {
  newSubCategoryId: string
  subCategories: SubcategoryResponseModel[]
  setFieldValue: (
    field: string,
    value: any,
    shouldValidate?: boolean | undefined
  ) => Promise<void | FormikErrors<DetailsFormValues>>
}

export const onSubcategoryChange = async ({
  newSubCategoryId,
  subCategories,
  setFieldValue,
}: OnSubcategoryChangeProps) => {
  const newSubcategory = subCategories.find(
    (subcategory) => subcategory.id === newSubCategoryId
  )

  const { subcategoryConditionalFields } =
    buildSubcategoryConditonalFields(newSubcategory)
  await setFieldValue(
    'subcategoryConditionalFields',
    subcategoryConditionalFields
  )
}

export const buildVenueOptions = (venues: VenueListItemResponseModel[]) => {
  let venueOptions = venues
    .map((venue) => ({
      value: venue.id.toString(),
      label: computeVenueDisplayName(venue),
    }))
    .sort((a, b) => a.label.localeCompare(b.label, 'fr'))
  if (venueOptions.length !== 1) {
    venueOptions = [
      { value: '', label: 'Sélectionner un lieu' },
      ...venueOptions,
    ]
  }

  return venueOptions
}
