import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'

import type { QuantityPerPriceCategoryForm } from '../components/StocksCalendar/form/types'

export type IndividualOfferTimetableFormValues = {
  timetableType: 'calendar' | 'openingHours'
  hasEndDate: 'yes' | 'no'
  hasStartDate: 'yes' | 'no'
  startDate?: string
  endDate?: string
  openingHours?: WeekdayOpeningHoursTimespans | null
  quantityPerPriceCategories?: QuantityPerPriceCategoryForm[]
}
