import * as PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import DatePicker from 'react-datepicker'

import InputWithCalendar from 'components/layout/inputs/PeriodSelector/InputWithCalendar'
import {
  getLocalDepartementDateTimeFromUtc,
  getUtcDateTimeFromLocalDepartement,
} from 'utils/timezone'

const DateInput = ({
  ariaLabel,
  departmentCode,
  disabled,
  inError,
  maxUtcDateIsoFormat,
  minUtcDateIsoFormat,
  openingUtcDateIsoFormat,
  onChange,
  utcDateIsoFormat,
}) => {
  const getDepartementDateTime = date => {
    if (date) {
      return getLocalDepartementDateTimeFromUtc(date, departmentCode)
    }
    return undefined
  }

  const selectedDate = getDepartementDateTime(utcDateIsoFormat)

  const onChangeWrapper = useCallback(
    dateTimeInDepartementTimezone => {
      if (dateTimeInDepartementTimezone) {
        const dateTimeInUtcTimezone = getUtcDateTimeFromLocalDepartement(
          dateTimeInDepartementTimezone,
          departmentCode
        )
        onChange(dateTimeInUtcTimezone)
      } else {
        onChange(null)
      }
    },
    [departmentCode, onChange]
  )

  return (
    <DatePicker
      className="datetime-input"
      customInput={(
        <InputWithCalendar
          ariaLabel={ariaLabel}
          customClass={`field-date-only${disabled ? ' disabled' : ''}${inError ? ' error' : ''}`}
        />
      )}
      dateFormat="dd/MM/yyyy"
      disabled={disabled}
      dropdownMode="scroll"
      maxDate={getDepartementDateTime(maxUtcDateIsoFormat)}
      minDate={getDepartementDateTime(minUtcDateIsoFormat)}
      onChange={onChangeWrapper}
      openToDate={selectedDate ? selectedDate : getDepartementDateTime(openingUtcDateIsoFormat)}
      placeholderText="JJ/MM/AAAA"
      selected={selectedDate}
    />
  )
}

DateInput.defaultProps = {
  ariaLabel: undefined,
  departmentCode: '',
  disabled: false,
  inError: false,
  maxUtcDateIsoFormat: undefined,
  minUtcDateIsoFormat: undefined,
  utcDateIsoFormat: null,
}

DateInput.propTypes = {
  ariaLabel: PropTypes.string,
  departmentCode: PropTypes.string,
  disabled: PropTypes.bool,
  inError: PropTypes.bool,
  maxUtcDateIsoFormat: PropTypes.string,
  minUtcDateIsoFormat: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  openingUtcDateIsoFormat: PropTypes.string.isRequired,
  utcDateIsoFormat: PropTypes.string,
}

export default DateInput
