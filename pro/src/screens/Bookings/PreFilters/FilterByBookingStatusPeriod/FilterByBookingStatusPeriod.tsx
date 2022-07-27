import { addDays, subDays } from 'date-fns'
import React from 'react'

import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import { DEFAULT_BOOKING_PERIOD, TPreFilters } from 'core/Bookings'
import { getToday } from 'utils/date'

import styles from './FilterByBookingStatusPeriod.module.scss'
import FilterByStatus from './FilterByStatus'

interface IFilterByBookingStatusPeriodProps {
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
}: IFilterByBookingStatusPeriodProps): JSX.Element => {
  function handleBookingBeginningDateChange(bookingBeginningDate: Date) {
    updateFilters({
      bookingBeginningDate: bookingBeginningDate
        ? bookingBeginningDate
        : selectedBookingEndingDate
        ? subDays(selectedBookingEndingDate, DEFAULT_BOOKING_PERIOD)
        : undefined,
    })
  }

  function handleBookingEndingDateChange(bookingEndingDate: Date) {
    updateFilters({
      bookingEndingDate: bookingEndingDate
        ? bookingEndingDate
        : selectedBookingBeginningDate
        ? addDays(selectedBookingBeginningDate, DEFAULT_BOOKING_PERIOD)
        : undefined,
    })
  }

  return (
    <div className={styles['satus-period-filter']}>
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
        todayDate={getToday()}
      />
    </div>
  )
}

export default FilterByBookingStatusPeriod
