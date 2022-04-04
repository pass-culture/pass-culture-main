/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import { addDays, subDays } from 'date-fns'
import React from 'react'

import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import { DEFAULT_BOOKING_PERIOD } from 'core/Bookings'
import { getToday } from 'utils/date'

import styles from './FilterByBookingStatusPeriod.module.scss'
import FilterByStatus from './FilterByStatus'

interface IPreFiltersProp {
  bookingBeginningDate?: Date
  bookingEndingDate?: Date
  bookingStatusFilter: string
  offerEventDate: Date
  offerVenueId: string
}
interface IFilterByBookingStatusPeriodProps {
  isDisabled: boolean
  selectedBookingBeginningDate?: Date
  selectedBookingEndingDate?: Date
  selectedBookingFilter: string
  updateFilters: (filters: Partial<IPreFiltersProp>) => void
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
      <div className="vertical-bar" />
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
