import React from 'react'
import moment from 'moment/moment'
import InputWithCalendar from './InputWithCalendar'
import DatePicker from 'react-datepicker'
import PropTypes from 'prop-types'
import { EMPTY_FILTER_VALUE } from './Filters'

const FilterByBookingPeriod = ({
  isDisabled,
  oldestBookingDate,
  updateFilters,
  selectedBookingBeginningDate,
  selectedBookingEndingDate,
}) => {
  function handleBookingBeginningDateChange(bookingBeginningDate) {
    const dateToFilter =
      bookingBeginningDate === null ? EMPTY_FILTER_VALUE : bookingBeginningDate.format('YYYY-MM-DD')
    const updatedFilter = { bookingBeginningDate: dateToFilter }
    const updatedSelectedContent = { selectedBookingBeginningDate: bookingBeginningDate }
    updateFilters(updatedFilter, updatedSelectedContent)
  }

  function handleBookingEndingDateChange(bookingEndingDate) {
    const dateToFilter =
      bookingEndingDate === null ? EMPTY_FILTER_VALUE : bookingEndingDate.format('YYYY-MM-DD')
    const updatedFilter = { bookingEndingDate: dateToFilter }
    const updatedSelectedContent = { selectedBookingEndingDate: bookingEndingDate }
    updateFilters(updatedFilter, updatedSelectedContent)
  }

  return (
    <div className="fw-booking-date">
      <label
        className="fw-booking-date-label"
        htmlFor="select-filter-booking-date"
      >
        {'Période de réservation'}
      </label>
      <div
        className={`fw-booking-date-inputs ${isDisabled ? 'disabled' : ''}`}
        id="select-filter-booking-date"
      >
        <div className="fw-booking-date-begin-picker">
          <DatePicker
            className="fw-booking-date-input"
            customInput={
              <InputWithCalendar
                customClass={`field-date-only field-date-begin ${isDisabled ? 'disabled' : ''}`}
              />
            }
            disabled={isDisabled}
            dropdownMode="select"
            maxDate={selectedBookingEndingDate}
            minDate={oldestBookingDate}
            onChange={handleBookingBeginningDateChange}
            placeholderText="JJ/MM/AAAA"
            selected={selectedBookingBeginningDate}
          />
        </div>
        <span className="vertical-bar" />
        <div className="fw-booking-date-end-picker">
          <DatePicker
            className="fw-booking-date-input"
            customInput={
              <InputWithCalendar
                customClass={`field-date-only field-date-end ${isDisabled ? 'disabled' : ''}`}
              />
            }
            disabled={isDisabled}
            dropdownMode="select"
            maxDate={moment()}
            minDate={selectedBookingBeginningDate}
            onChange={handleBookingEndingDateChange}
            placeholderText="JJ/MM/AAAA"
            selected={selectedBookingEndingDate}
          />
        </div>
      </div>
    </div>
  )
}

FilterByBookingPeriod.propTypes = {
  isDisabled: PropTypes.bool.isRequired,
  oldestBookingDate: PropTypes.string.isRequired,
  selectedBookingBeginningDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string])
    .isRequired,
  selectedBookingEndingDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string]).isRequired,
  updateFilters: PropTypes.func.isRequired,
}

export default FilterByBookingPeriod
