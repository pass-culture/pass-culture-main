import moment from 'moment'
import * as PropTypes from 'prop-types'
import React from 'react'
import DatePicker from 'react-datepicker'

import InputWithCalendar from 'components/layout/inputs/PeriodSelector/InputWithCalendar'
import { formatLocalTimeDateString } from 'utils/timezone'

export const TimeInput = ({
  ariaLabel,
  departmentCode,
  disabled,
  maxUtcDateIsoFormat,
  minUtcDateIsoFormat,
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

  return (
    <DatePicker
      className="datetime-input"
      customInput={(
        <InputWithCalendar
          ariaLabel={ariaLabel}
          customClass={`field-date-only without-icon ${disabled ? 'disabled' : ''}`}
        />
      )}
      dateFormat="HH:mm"
      disabled={disabled}
      maxDate={getMomentDate(maxUtcDateIsoFormat)}
      minDate={getMomentDate(minUtcDateIsoFormat)}
      onChange={onChange}
      placeholderText="HH:MM"
      selected={getMomentDate(utcDateIsoFormat)}
      showTimeSelect
      showTimeSelectOnly
      timeCaption="Heure"
      timeFormat="HH:mm"
      timeIntervals={15}
    />
  )
}

TimeInput.defaultProps = {
  ariaLabel: undefined,
  disabled: false,
  maxUtcDateIsoFormat: undefined,
  minUtcDateIsoFormat: undefined,
}

TimeInput.propTypes = {
  ariaLabel: PropTypes.string,
  departmentCode: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  maxUtcDateIsoFormat: PropTypes.string,
  minUtcDateIsoFormat: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  utcDateIsoFormat: PropTypes.string.isRequired,
}
