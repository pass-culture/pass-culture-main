import PropTypes from 'prop-types'
import React from 'react'
import DatePicker from 'react-datepicker'

import InputWithCalendar from './InputWithCalendar'

const PeriodSelector = ({
  changePeriodBeginningDateValue,
  changePeriodEndingDateValue,
  isDisabled,
  label,
  maxDateEnding,
  minDateBeginning,
  periodBeginningDate,
  periodEndingDate,
  todayDate,
}) => {
  return (
    <div className="period-filter">
      <label
        className="period-filter-label"
        htmlFor="select-filter-date"
      >
        {label}
      </label>
      <div
        className={`period-filter-inputs ${isDisabled ? 'disabled' : ''}`}
        id="select-filter-date"
      >
        <div className="period-filter-begin-picker">
          <DatePicker
            className="period-filter-input"
            customInput={(
              <InputWithCalendar
                customClass={`field-date-only field-date-begin ${isDisabled ? 'disabled' : ''}`}
              />
            )}
            dateFormat="dd/MM/yyyy"
            disabled={isDisabled}
            dropdownMode="select"
            maxDate={periodEndingDate ? periodEndingDate : undefined}
            minDate={minDateBeginning ? minDateBeginning : undefined}
            onChange={changePeriodBeginningDateValue}
            openToDate={periodBeginningDate ? periodBeginningDate : todayDate}
            placeholderText="JJ/MM/AAAA"
            selected={periodBeginningDate ? periodBeginningDate : undefined}
          />
        </div>
        <span className="vertical-bar" />
        <div className="period-filter-end-picker">
          <DatePicker
            className="period-filter-input"
            customInput={(
              <InputWithCalendar
                customClass={`field-date-only field-date-end ${isDisabled ? 'disabled' : ''}`}
              />
            )}
            dateFormat="dd/MM/yyyy"
            disabled={isDisabled}
            dropdownMode="select"
            maxDate={maxDateEnding ? maxDateEnding : undefined}
            minDate={periodBeginningDate ? periodBeginningDate : undefined}
            onChange={changePeriodEndingDateValue}
            openToDate={periodEndingDate ? periodEndingDate : todayDate}
            placeholderText="JJ/MM/AAAA"
            selected={periodEndingDate ? periodEndingDate : undefined}
          />
        </div>
      </div>
    </div>
  )
}

PeriodSelector.defaultProps = {
  maxDateEnding: undefined,
  minDateBeginning: undefined,
  periodBeginningDate: undefined,
  periodEndingDate: undefined,
}

PeriodSelector.propTypes = {
  changePeriodBeginningDateValue: PropTypes.func.isRequired,
  changePeriodEndingDateValue: PropTypes.func.isRequired,
  isDisabled: PropTypes.bool.isRequired,
  label: PropTypes.string.isRequired,
  maxDateEnding: PropTypes.string,
  minDateBeginning: PropTypes.string,
  periodBeginningDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string]),
  periodEndingDate: PropTypes.oneOfType([PropTypes.shape(), PropTypes.string]),
  todayDate: PropTypes.shape().isRequired,
}

export default PeriodSelector
