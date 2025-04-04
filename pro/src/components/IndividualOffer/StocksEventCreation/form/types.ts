import { StocksOrderedBy } from 'apiClient/v1'

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

//  Under WIP_ENABLE_EVENT_WITH_OPENING_HOUR FF
export enum DurationTypeOption {
  ONE_DAY = 'ONE_DAY',
  MULTIPLE_DAYS_WEEKS = 'MULTIPLE_DAYS_WEEKS',
}

export enum TimeSlotTypeOption {
  SPECIFIC_TIME = 'SPECIFIC_TIME',
  OPENING_HOURS = 'OPENING_HOURS',
}

export type StocksCalendarFormValues = {
  durationType: DurationTypeOption
  oneDayDate?: string
  multipleDaysStartDate?: string
  multipleDaysEndDate?: string
  multipleDaysHasNoEndDate: boolean
  multipleDaysWeekDays: {
    label: string
    value: RecurrenceDays
    checked: boolean
  }[]
  timeSlotType: TimeSlotTypeOption
  specificTimeSlots: { slot: string }[]
  pricingCategoriesQuantities: {
    quantity?: number
    isUnlimited?: boolean
    priceCategory: string
  }[]
  bookingLimitDateInterval?: number
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
