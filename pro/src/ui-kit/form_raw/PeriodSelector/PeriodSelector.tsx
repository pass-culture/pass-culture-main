import React from 'react'

import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'

interface PeriodSelectorProps {
  onBeginningDateChange: (date: string) => void
  onEndingDateChange: (date: string) => void
  isDisabled?: boolean
  label?: string
  maxDateEnding?: Date
  minDateBeginning?: Date
  periodBeginningDate: string
  periodEndingDate: string
}

const PeriodSelector = ({
  onBeginningDateChange,
  onEndingDateChange,
  isDisabled,
  label,
  maxDateEnding,
  minDateBeginning,
  periodBeginningDate,
  periodEndingDate,
}: PeriodSelectorProps) => (
  <div className="period-filter">
    <div className="period-filter-label">
      {label}
      <div className={`period-filter-inputs ${isDisabled ? 'disabled' : ''}`}>
        <div className="period-filter-begin-picker">
          <BaseDatePicker
            className="period-filter-input field-date-begin"
            aria-label="Début de la période"
            disabled={isDisabled}
            maxDate={new Date(periodEndingDate)}
            minDate={minDateBeginning}
            onChange={event => onBeginningDateChange(event.target.value)}
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
            minDate={new Date(periodBeginningDate)}
            onChange={event => onEndingDateChange(event.target.value)}
            value={periodEndingDate}
          />
        </div>
      </div>
    </div>
  </div>
)

export default PeriodSelector
