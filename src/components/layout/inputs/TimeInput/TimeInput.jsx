import * as PropTypes from 'prop-types'
import React, { useCallback } from 'react'
import DatePicker from 'react-datepicker'

import InputWithCalendar from 'components/layout/inputs/PeriodSelector/InputWithCalendar'
import {
  getLocalDepartementDateTimeFromUtc,
  getUtcDateTimeFromLocalDepartement,
} from 'utils/timezone'

const TimeInput = ({
  ariaLabel,
  departmentCode,
  disabled,
  inError,
  onChange,
  utcDateIsoFormat,
}) => {
  const getDepartementDate = date => {
    if (date) {
      return getLocalDepartementDateTimeFromUtc(date, departmentCode)
    }
    return undefined
  }

  const onChangeWrapper = useCallback(
    zonedDate => {
      if (zonedDate) {
        const utcDate = getUtcDateTimeFromLocalDepartement(zonedDate, departmentCode)
        onChange(utcDate)
      } else {
        onChange(zonedDate)
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
          customClass={`field-date-only without-icon${disabled ? ' disabled' : ''}${
            inError ? ' error' : ''
          }`}
        />
      )}
      dateFormat="HH:mm"
      disabled={disabled}
      dropdownMode="scroll"
      onChange={onChangeWrapper}
      placeholderText="HH:MM"
      selected={getDepartementDate(utcDateIsoFormat)}
      showTimeSelect
      showTimeSelectOnly
      timeCaption="Horaire"
      timeFormat="HH:mm"
      timeIntervals={15}
    />
  )
}

TimeInput.defaultProps = {
  ariaLabel: undefined,
  disabled: false,
  inError: false,
}

TimeInput.propTypes = {
  ariaLabel: PropTypes.string,
  departmentCode: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  inError: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
  utcDateIsoFormat: PropTypes.string.isRequired,
}

export default TimeInput
