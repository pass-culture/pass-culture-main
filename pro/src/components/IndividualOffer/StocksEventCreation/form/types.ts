import { type EnumType } from 'commons/custom_types/utils'

export const RecurrenceType = {
  UNIQUE: 'UNIQUE',
  DAILY: 'DAILY',
  WEEKLY: 'WEEKLY',
  MONTHLY: 'MONTHLY',
} as const
// eslint-disable-next-line no-redeclare
export type RecurrenceType = EnumType<typeof RecurrenceType>

export const RecurrenceDays = {
  MONDAY: 'monday',
  TUESDAY: 'tuesday',
  WEDNESDAY: 'wednesday',
  THURSDAY: 'thursday',
  FRIDAY: 'friday',
  SATURDAY: 'saturday',
  SUNDAY: 'sunday',
} as const
// eslint-disable-next-line no-redeclare
export type RecurrenceDays = EnumType<typeof RecurrenceDays>

export const MonthlyOption = {
  X_OF_MONTH: 'X_OF_MONTH',
  BY_FIRST_DAY: 'BY_FIRST_DAY',
  BY_LAST_DAY: 'BY_LAST_DAY',
} as const
// eslint-disable-next-line no-redeclare
export type MonthlyOption = EnumType<typeof MonthlyOption>

export type QuantityPerPriceCategoryForm = {
  quantity: number | ''
  priceCategory: string
}

export type RecurrenceFormValues = {
  recurrenceType: string
  days: RecurrenceDays[]
  startingDate: string
  endingDate: string
  beginningTimes: string[]
  quantityPerPriceCategories: QuantityPerPriceCategoryForm[]
  bookingLimitDateInterval: number | ''
  monthlyOption: MonthlyOption | null
}
