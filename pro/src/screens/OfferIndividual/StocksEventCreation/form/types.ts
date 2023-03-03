import type { FormikProps } from 'formik'

export enum RecurrenceType {
  UNIQUE = 'UNIQUE',
  DAILY = 'DAILY',
  WEEKLY = 'WEEKLY',
  MONTHLY = 'MONTHLY',
}

export type QuantityPerPriceCategoryForm = {
  quantity: number | ''
  priceCategory: string
}

export type RecurrenceFormValues = {
  recurrenceType: string
  startingDate: Date | null
  beginningTimes: (Date | null)[]
  quantityPerPriceCategories: QuantityPerPriceCategoryForm[]
  bookingLimitDateInterval: number | ''
}

export type PriceCategoriesFormType = FormikProps<RecurrenceFormValues>
