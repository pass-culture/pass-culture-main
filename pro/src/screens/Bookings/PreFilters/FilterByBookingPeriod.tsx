import { addDays, subDays } from 'date-fns'
import React from 'react'

import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import { DEFAULT_BOOKING_PERIOD, TPreFilters } from 'core/Bookings'
import { getToday } from 'utils/date'

interface IFilterByBookingPeriodProps {
  isDisabled?: boolean
  updateFilters: (filters: Partial<TPreFilters>) => void
  selectedBookingBeginningDate: Date
  selectedBookingEndingDate: Date
}

const FilterByBookingPeriod = ({
  isDisabled,
  updateFilters,
  selectedBookingBeginningDate,
  selectedBookingEndingDate,
}: IFilterByBookingPeriodProps): JSX.Element => {
  function handleBookingBeginningDateChange(bookingBeginningDate: Date) {
    updateFilters({
      bookingBeginningDate: bookingBeginningDate
        ? bookingBeginningDate
        : subDays(selectedBookingEndingDate, DEFAULT_BOOKING_PERIOD),
    })
  }

  function handleBookingEndingDateChange(bookingEndingDate: Date) {
    updateFilters({
      bookingEndingDate: bookingEndingDate
        ? bookingEndingDate
        : addDays(selectedBookingBeginningDate, DEFAULT_BOOKING_PERIOD),
    })
  }

  return (
    <PeriodSelector
      changePeriodBeginningDateValue={handleBookingBeginningDateChange}
      changePeriodEndingDateValue={handleBookingEndingDateChange}
      isDisabled={isDisabled}
      label="Période de réservation"
      maxDateEnding={getToday()}
      periodBeginningDate={selectedBookingBeginningDate || undefined}
      periodEndingDate={selectedBookingEndingDate}
      todayDate={getToday()}
    />
  )
}

export default FilterByBookingPeriod
