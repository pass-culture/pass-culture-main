import { getCalendarProvider } from '../../../utils'
import DatePickerField from '../../../../../forms/inputs/DatePickerField/DatePickerField'
import moment from 'moment'
import React from 'react'
import PropTypes from 'prop-types'

const BookingDatePickerField = (handleOnChange, values) => (fieldParams) => {
  const { input } = fieldParams
  const calendarDates = getCalendarProvider(values)
  const calendarLabel = calendarDates.length === 1 ? '' : 'Choisissez une date'
  const selectedValue = (input.value && input.value.date) || null
  const dateFormat = 'DD MMMM YYYY'

  return (
    <DatePickerField
      {...input}
      className="text-center mb36"
      dateFormat={dateFormat}
      hideToday
      id="booking-form-date-picker-field"
      label={calendarLabel}
      name="date"
      onChange={handleOnChange(input)}
      placeholder={moment().format(dateFormat)}
      popperPlacement="bottom"
      provider={calendarDates}
      readOnly={calendarDates.length === 1}
      selected={selectedValue}
    />
  )
}

BookingDatePickerField.propTypes = {
  handleChange: PropTypes.func.isRequired,
  values: PropTypes.shape().isRequired,
}

export default BookingDatePickerField
