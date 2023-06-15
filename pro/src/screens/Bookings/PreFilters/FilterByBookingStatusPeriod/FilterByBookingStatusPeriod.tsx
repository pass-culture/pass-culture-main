import { addDays, subDays } from 'date-fns'
import React from 'react'

import { DEFAULT_BOOKING_PERIOD, TPreFilters } from 'core/Bookings'
import PeriodSelector from 'ui-kit/form_raw/PeriodSelector/PeriodSelector'
import { getToday } from 'utils/date'

import styles from './FilterByBookingStatusPeriod.module.scss'
import FilterByStatus from './FilterByStatus'

interface FilterByBookingStatusPeriodProps {
  isDisabled: boolean
  selectedBookingBeginningDate?: Date
  selectedBookingEndingDate?: Date
  selectedBookingFilter: string
  updateFilters: (filters: Partial<TPreFilters>) => void
}

const FilterByBookingStatusPeriod = ({
  isDisabled = false,
  selectedBookingBeginningDate,
  selectedBookingEndingDate,
  selectedBookingFilter,
  updateFilters,
}: FilterByBookingStatusPeriodProps): JSX.Element => {
  const handleBookingBeginningDateChange = (bookingBeginningDate: Date) => {
    updateFilters({
      bookingBeginningDate: bookingBeginningDate
        ? bookingBeginningDate
        : selectedBookingEndingDate
        ? subDays(selectedBookingEndingDate, DEFAULT_BOOKING_PERIOD)
        : undefined,
    })
  }

  const handleBookingEndingDateChange = (bookingEndingDate: Date) => {
    updateFilters({
      bookingEndingDate: bookingEndingDate
        ? bookingEndingDate
        : selectedBookingBeginningDate
        ? addDays(selectedBookingBeginningDate, DEFAULT_BOOKING_PERIOD)
        : undefined,
    })
  }

  return (
    <div className={styles['status-period-filter']}>
      <FilterByStatus
        isDisabled={isDisabled}
        selectedStatusId={selectedBookingFilter}
        updateFilters={updateFilters}
      />

      <PeriodSelector
        changePeriodBeginningDateValue={handleBookingBeginningDateChange}
        changePeriodEndingDateValue={handleBookingEndingDateChange}
        isDisabled={isDisabled}
        maxDateEnding={getToday()}
        periodBeginningDate={selectedBookingBeginningDate || undefined}
        periodEndingDate={selectedBookingEndingDate}
      />
    </div>
  )
}

export default FilterByBookingStatusPeriod
