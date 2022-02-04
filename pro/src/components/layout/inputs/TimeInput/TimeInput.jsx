import fr from 'date-fns/locale/fr'
import * as PropTypes from 'prop-types'
import React from 'react'
import DatePicker, { registerLocale } from 'react-datepicker'

import InputWithCalendar from 'components/layout/inputs/PeriodSelector/InputWithCalendar'

registerLocale('fr', fr)

const TimeInput = ({ ariaLabel, disabled, inError, onChange, dateTime }) => {
  return (
    <DatePicker
      className="datetime-input"
      customInput={
        <InputWithCalendar
          ariaLabel={ariaLabel}
          customClass={`field-date-only without-icon${
            disabled ? ' disabled' : ''
          }${inError ? ' error' : ''}`}
        />
      }
      dateFormat="HH:mm"
      disabled={disabled}
      dropdownMode="scroll"
      locale="fr"
      onChange={onChange}
      placeholderText="HH:MM"
      selected={dateTime}
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
  dateTime: null,
  disabled: false,
  inError: false,
}

TimeInput.propTypes = {
  ariaLabel: PropTypes.string,
  dateTime: PropTypes.instanceOf(Date),
  disabled: PropTypes.bool,
  inError: PropTypes.bool,
  onChange: PropTypes.func.isRequired,
}

export default TimeInput
