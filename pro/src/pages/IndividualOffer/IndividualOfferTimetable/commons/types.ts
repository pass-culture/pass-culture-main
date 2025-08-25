import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'

import type { QuantityPerPriceCategoryForm } from '../components/StocksCalendar/form/types'

export type IndividualOfferTimetableFormValues = {
    timetableType: 'calendar' | 'openingHours'
    startDate?: string
    noEndDate: boolean
    endDate?: string
    openingHours?: WeekdayOpeningHoursTimespans | null
    quantityPerPriceCategories?: QuantityPerPriceCategoryForm[]
}
