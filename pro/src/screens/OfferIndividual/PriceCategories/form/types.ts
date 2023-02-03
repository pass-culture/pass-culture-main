import type { FormikProps } from 'formik'

import { hasProperties } from 'utils/types'

export type PriceCategoryForm = {
  label: string
  price: number | ''
  id?: number
}

export type PriceCategoriesFormValues = {
  priceCategories: PriceCategoryForm[]
  isDuo: boolean
}

export const isPriceCategoriesFormValues = (
  value: unknown
): value is PriceCategoriesFormValues =>
  hasProperties(value, ['priceCategories', 'isDuo'])

export type PriceCategoriesFormType = FormikProps<PriceCategoriesFormValues>
