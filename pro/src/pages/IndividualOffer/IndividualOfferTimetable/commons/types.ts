import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'

import type { QuantityPerPriceCategoryForm } from '../components/StocksCalendar/form/types'

//  TODO : Could be replaced with a boolean value in the forms ?
export enum HasDateEnum {
  YES = 'yes',
  NO = 'no',
}

export type IndividualOfferTimetableFormValues = {
  timetableType: 'calendar' | 'openingHours'
  hasEndDate: HasDateEnum
  hasStartDate: HasDateEnum
  startDate: string | null
  endDate: string | null
  openingHours?: WeekdayOpeningHoursTimespans | null
  quantityPerPriceCategories?: QuantityPerPriceCategoryForm[]
}
