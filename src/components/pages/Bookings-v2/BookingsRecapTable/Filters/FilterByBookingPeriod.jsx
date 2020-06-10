import React from 'react'
import moment from 'moment/moment'
import InputWithCalendar from './InputWithCalendar'
import DatePicker from 'react-datepicker'
import PropTypes from 'prop-types'

const FilterByBookingPeriod = ({
  oldestBookingDate,
  onHandleBookingBeginningDateChange,
  onHandleBookingEndingDateChange,
  selectedBookingBeginningDate,
  selectedBookingEndingDate,
}) => {
  return (
    <div className="fw-booking-date">
      <label
        className="fw-booking-date-label"
        htmlFor="select-filter-booking-date"
      >
        {'Période de réservation'}
      </label>
      <div
        className="fw-booking-date-inputs"
        id="select-filter-booking-date"
      >
        <div className="fw-booking-date-begin-picker">
          <DatePicker
            className="fw-booking-date-input"
            customInput={<InputWithCalendar customClass="field-date-only field-date-begin" />}
            dropdownMode="select"
            maxDate={selectedBookingEndingDate}
            minDate={oldestBookingDate}
            onChange={onHandleBookingBeginningDateChange}
            placeholderText="JJ/MM/AAAA"
            selected={selectedBookingBeginningDate}
          />
        </div>
        <span className="vertical-bar" />
        <div className="fw-booking-date-end-picker">
          <DatePicker
            className="fw-booking-date-input"
            customInput={<InputWithCalendar customClass="field-date-only field-date-end" />}
            dropdownMode="select"
            maxDate={moment()}
            minDate={selectedBookingBeginningDate}
            onChange={onHandleBookingEndingDateChange}
            placeholderText="JJ/MM/AAAA"
            selected={selectedBookingEndingDate}
          />
        </div>
      </div>
    </div>
  )
}

FilterByBookingPeriod.propTypes = {
  oldestBookingDate: PropTypes.string.isRequired,
  onHandleBookingBeginningDateChange: PropTypes.func.isRequired,
  onHandleBookingEndingDateChange: PropTypes.func.isRequired,
  selectedBookingBeginningDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string])
    .isRequired,
  selectedBookingEndingDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string]).isRequired,
}

export default FilterByBookingPeriod
