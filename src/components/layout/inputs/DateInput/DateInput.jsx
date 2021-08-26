/*
* @debt directory "Gaël: this file should be migrated within the new directory structure"
*/

import * as PropTypes from 'prop-types'
import React from 'react'
import DatePicker from 'react-datepicker'

import InputWithCalendar from 'components/layout/inputs/PeriodSelector/InputWithCalendar'

const DateInput = ({
  ariaLabel,
  disabled,
  inError,
  maxDateTime,
  minDateTime,
  openingDateTime,
  onChange,
  dateTime,
}) => {
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
      maxDate={maxDateTime}
      minDate={minDateTime}
      onChange={onChange}
      openToDate={dateTime ? dateTime : openingDateTime}
      placeholderText="JJ/MM/AAAA"
      selected={dateTime}
    />
  )
}

DateInput.defaultProps = {
  ariaLabel: undefined,
  dateTime: null,
  disabled: false,
  inError: false,
  maxDateTime: undefined,
  minDateTime: undefined,
  openingDateTime: undefined,
}

DateInput.propTypes = {
  ariaLabel: PropTypes.string,
  dateTime: PropTypes.instanceOf(Date),
  disabled: PropTypes.bool,
  inError: PropTypes.bool,
  maxDateTime: PropTypes.instanceOf(Date),
  minDateTime: PropTypes.instanceOf(Date),
  onChange: PropTypes.func.isRequired,
  openingDateTime: PropTypes.instanceOf(Date),
}

export default DateInput
