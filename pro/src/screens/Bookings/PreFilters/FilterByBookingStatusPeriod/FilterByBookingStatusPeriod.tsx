import React from 'react'

import { PreFiltersParams } from 'core/Bookings/types'
import PeriodSelector from 'ui-kit/form_raw/PeriodSelector/PeriodSelector'

import styles from './FilterByBookingStatusPeriod.module.scss'
import FilterByStatus from './FilterByStatus'

interface FilterByBookingStatusPeriodProps {
  isDisabled: boolean
  selectedBookingBeginningDate: string
  selectedBookingEndingDate: string
  selectedBookingFilter: string
  updateFilters: (filters: Partial<PreFiltersParams>) => void
}

const FilterByBookingStatusPeriod = ({
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
    <div className={styles['status-period-filter']}>
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
    </div>
  )
}

export default FilterByBookingStatusPeriod
