import moment from 'moment'
import * as PropTypes from 'prop-types'
import React from 'react'
import DatePicker from 'react-datepicker'

import InputWithCalendar from 'components/layout/inputs/PeriodSelector/InputWithCalendar'
import { formatLocalTimeDateString } from 'utils/timezone'

const DateInput = ({
  ariaLabel,
  departmentCode,
  disabled,
  maxUtcDateIsoFormat,
  minUtcDateIsoFormat,
  openingUtcDateIsoFormat,
  onChange,
  utcDateIsoFormat,
}) => {
  const getMomentDate = date => {
    if (date) {
      const timezonedDateIsoFormat = formatLocalTimeDateString(
        date,
        departmentCode,
        'YYYY-MM-DD HH:mm'
      )
      return moment(timezonedDateIsoFormat)
    }
    return undefined
  }

  const selectedDate = getMomentDate(utcDateIsoFormat)

  return (
    <DatePicker
      className="datetime-input"
      customInput={(
        <InputWithCalendar
          ariaLabel={ariaLabel}
          customClass={`field-date-only ${disabled ? 'disabled' : ''}`}
        />
      )}
      disabled={disabled}
      maxDate={getMomentDate(maxUtcDateIsoFormat)}
      minDate={getMomentDate(minUtcDateIsoFormat)}
      onChange={onChange}
      openToDate={selectedDate ? selectedDate : getMomentDate(openingUtcDateIsoFormat)}
      placeholderText="JJ/MM/AAAA"
      selected={getMomentDate(utcDateIsoFormat)}
    />
  )
}

DateInput.defaultProps = {
  ariaLabel: undefined,
  disabled: false,
  maxUtcDateIsoFormat: undefined,
  minUtcDateIsoFormat: undefined,
}

DateInput.propTypes = {
  ariaLabel: PropTypes.string,
  departmentCode: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  maxUtcDateIsoFormat: PropTypes.string,
  minUtcDateIsoFormat: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  openingUtcDateIsoFormat: PropTypes.string.isRequired,
  utcDateIsoFormat: PropTypes.string.isRequired,
}

export default DateInput
