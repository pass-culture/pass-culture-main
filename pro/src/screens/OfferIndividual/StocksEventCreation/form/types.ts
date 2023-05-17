import type { FormikProps } from 'formik'

export enum RecurrenceType {
  UNIQUE = 'UNIQUE',
  DAILY = 'DAILY',
  WEEKLY = 'WEEKLY',
  MONTHLY = 'MONTHLY',
}

export enum RecurrenceDays {
  MONDAY = 'monday',
  TUESDAY = 'tuesday',
  WEDNESDAY = 'wednesday',
  THURSDAY = 'thursday',
  FRIDAY = 'friday',
  SATURDAY = 'saturday',
  SUNDAY = 'sunday',
}

export type QuantityPerPriceCategoryForm = {
  quantity: number | ''
  priceCategory: string
}

export type RecurrenceFormValues = {
  recurrenceType: string
  days: RecurrenceDays[]
  startingDate: Date | null
  endingDate: Date | null
  beginningTimes: (Date | null)[]
  quantityPerPriceCategories: QuantityPerPriceCategoryForm[]
  bookingLimitDateInterval: number | ''
}

export type PriceCategoriesFormType = FormikProps<RecurrenceFormValues>
