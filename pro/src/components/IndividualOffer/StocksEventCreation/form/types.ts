import { StocksOrderedBy } from '@/apiClient/v1'

export interface StocksEvent {
  id: number
  beginningDatetime: string
  bookingLimitDatetime: string
  priceCategoryId: number
  quantity: number | null
  bookingsQuantity: number
  isEventDeletable: boolean
}

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

export enum MonthlyOption {
  X_OF_MONTH = 'X_OF_MONTH',
  BY_FIRST_DAY = 'BY_FIRST_DAY',
  BY_LAST_DAY = 'BY_LAST_DAY',
}

export type QuantityPerPriceCategoryForm = {
  quantity?: number | null
  priceCategory: string
}

export type RecurrenceFormValues = {
  recurrenceType: RecurrenceType
  days: RecurrenceDays[]
  startingDate: string | null
  endingDate?: string | null
  beginningTimes: { beginningTime: string }[]
  quantityPerPriceCategories: QuantityPerPriceCategoryForm[]
  bookingLimitDateInterval: number | null
  monthlyOption?: MonthlyOption | null
}

export type StocksTableFilters = {
  date?: string
  time?: string
  priceCategoryId?: string
}

export type StocksTableSort = {
  sort?: StocksOrderedBy
  orderByDesc?: boolean
}
