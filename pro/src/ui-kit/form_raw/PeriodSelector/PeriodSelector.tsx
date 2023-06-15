import React from 'react'

import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'

interface PeriodSelectorProps {
  changePeriodBeginningDateValue: (date: Date) => void
  changePeriodEndingDateValue: (date: Date) => void
  isDisabled?: boolean
  label?: string
  maxDateEnding?: Date
  minDateBeginning?: Date
  periodBeginningDate?: Date
  periodEndingDate?: Date
}

const PeriodSelector = ({
  changePeriodBeginningDateValue,
  changePeriodEndingDateValue,
  isDisabled,
  label,
  maxDateEnding,
  minDateBeginning,
  periodBeginningDate,
  periodEndingDate,
}: PeriodSelectorProps) => (
  <div className="period-filter">
    <div className="period-filter-label">
      {label && label}
      <div className={`period-filter-inputs ${isDisabled ? 'disabled' : ''}`}>
        <div className="period-filter-begin-picker">
          <BaseDatePicker
            className="period-filter-input field-date-begin"
            aria-label="Début de la période"
            disabled={isDisabled}
            maxDate={periodEndingDate}
            minDate={minDateBeginning}
            onChange={changePeriodBeginningDateValue}
            value={periodBeginningDate}
          />
        </div>

        <span className="vertical-bar" />

        <div className="period-filter-end-picker">
          <BaseDatePicker
            className="period-filter-input field-date-end"
            aria-label="Fin de la période"
            disabled={isDisabled}
            maxDate={maxDateEnding}
            minDate={periodBeginningDate}
            onChange={changePeriodEndingDateValue}
            value={periodEndingDate}
          />
        </div>
      </div>
    </div>
  </div>
)

export default PeriodSelector
