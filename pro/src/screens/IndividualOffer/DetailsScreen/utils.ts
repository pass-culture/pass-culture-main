import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { showOptionsTree } from 'core/Offers/categoriesSubTypes'
import { SelectOption } from 'custom_types/form'
import { DEFAULT_DETAILS_INTITIAL_VALUES } from './constants'
import { FormikErrors } from 'formik'
import { DetailsFormValues } from './types'

export const buildCategoryOptions = (
  categories: CategoryResponseModel[]
): SelectOption[] =>
  categories
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

export const getShowSubTypeOptions = (showType: string): SelectOption[] => {
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

export const buildSubcategoryFields = (
  subcategory?: SubcategoryResponseModel
): {
  subcategoryFields: string[]
} => {
  const subcategoryFields = [...new Set(subcategory?.conditionalFields)]
  const isEvent = Boolean(subcategory?.isEvent)

  if (isEvent) {
    subcategoryFields.push('durationMinutes')
  }

  return { subcategoryFields }
}

type onSubcategoryChangeProps = {
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
}: onSubcategoryChangeProps) => {
  const newSubcategory = subCategories.find(
    (subcategory) => subcategory.id === newSubCategoryId
  )

  const { subcategoryFields } = buildSubcategoryFields(newSubcategory)
  await setFieldValue('subcategoryConditionalFields', subcategoryFields)
}
