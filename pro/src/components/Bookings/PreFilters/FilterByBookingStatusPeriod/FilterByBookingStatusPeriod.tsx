import { PreFiltersParams } from '@/commons/core/Bookings/types'
import { PeriodSelector } from '@/ui-kit/form/PeriodSelector/PeriodSelector'

import styles from './FilterByBookingStatusPeriod.module.scss'
import { FilterByStatus } from './FilterByStatus'

interface FilterByBookingStatusPeriodProps {
  isDisabled: boolean
  selectedBookingBeginningDate: string
  selectedBookingEndingDate: string
  selectedBookingFilter: string
  updateFilters: (filters: Partial<PreFiltersParams>) => void
}

export const FilterByBookingStatusPeriod = ({
  isDisabled = false,
  selectedBookingBeginningDate,
  selectedBookingEndingDate,
  selectedBookingFilter,
  updateFilters,
}: FilterByBookingStatusPeriodProps): JSX.Element => {
  const handleBookingBeginningDateChange = (bookingBeginningDate: string) => {
    updateFilters({ bookingBeginningDate })
  }

  const handleBookingEndingDateChange = (bookingEndingDate: string) => {
    updateFilters({ bookingEndingDate })
  }

  return (
    <fieldset className={styles['status-period-filter']}>
      <legend className={styles['visually-hidden']}>Période</legend>
      <FilterByStatus
        isDisabled={isDisabled}
        selectedStatusId={selectedBookingFilter}
        updateFilters={updateFilters}
      />

      <PeriodSelector
        className={styles['status-period-filter-selector']}
        onBeginningDateChange={handleBookingBeginningDateChange}
        onEndingDateChange={handleBookingEndingDateChange}
        isDisabled={isDisabled}
        maxDateEnding={new Date()}
        periodBeginningDate={selectedBookingBeginningDate}
        periodEndingDate={selectedBookingEndingDate}
      />
    </fieldset>
  )
}
