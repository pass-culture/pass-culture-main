import type { FormikProps } from 'formik'

export enum RecurrenceType {
  UNIQUE = 'UNIQUE',
  DAILY = 'DAILY',
  WEEKLY = 'WEEKLY',
  MONTHLY = 'MONTHLY',
}

export type RecurrenceFormValues = {
  recurrenceType: string
  startingDate: string
  beginningTimes: string[]
  quantityPerPriceCategories: {
    quantity: number | ''
    priceCategory: string
  }[]
  bookingLimitDateInterval: number | ''
}

export type PriceCategoriesFormType = FormikProps<RecurrenceFormValues>
