// Don't know why but eslint doesn't like the import of FormikProps but it exists trust me
// eslint-disable-next-line import/named
import { FormikProps } from 'formik'

export type PriceCategoryForm = {
  label: string
  price: number | ''
  id?: number
}

export type PriceCategoriesFormValues = {
  priceCategories: PriceCategoryForm[]
  isDuo: boolean
}

export type PriceCategoriesFormType = FormikProps<PriceCategoriesFormValues>
