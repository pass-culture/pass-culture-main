import PropTypes from 'prop-types'
import React from 'react'

import PeriodSelector from 'components/layout/inputs/PeriodSelector/PeriodSelector'
import { getToday } from 'utils/date'

const FilterByBookingPeriod = ({
  updateFilters,
  selectedBookingBeginningDate,
  selectedBookingEndingDate,
}) => {
  function handleBookingBeginningDateChange(bookingBeginningDate) {
    updateFilters({ bookingBeginningDate: bookingBeginningDate })
  }

  function handleBookingEndingDateChange(bookingEndingDate) {
    updateFilters({ bookingEndingDate: bookingEndingDate })
  }

  return (
    <PeriodSelector
      changePeriodBeginningDateValue={handleBookingBeginningDateChange}
      changePeriodEndingDateValue={handleBookingEndingDateChange}
      label="Période de réservation"
      maxDateEnding={getToday()}
      periodBeginningDate={selectedBookingBeginningDate || undefined}
      periodEndingDate={selectedBookingEndingDate}
      todayDate={getToday()}
    />
  )
}

FilterByBookingPeriod.propTypes = {
  selectedBookingBeginningDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string])
    .isRequired,
  selectedBookingEndingDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string]).isRequired,
  updateFilters: PropTypes.func.isRequired,
}

export default FilterByBookingPeriod
