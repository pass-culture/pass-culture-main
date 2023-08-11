import cn from 'classnames'
import React from 'react'

import { BaseDatePicker } from 'ui-kit/form/DatePicker/BaseDatePicker'

import styles from './PeriodSelector.module.scss'

interface PeriodSelectorProps {
  className?: string
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
  className,
  onBeginningDateChange,
  onEndingDateChange,
  isDisabled,
  label,
  maxDateEnding,
  minDateBeginning,
  periodBeginningDate,
  periodEndingDate,
}: PeriodSelectorProps) => (
  <div className={styles['period-filter']}>
    <div className={styles['period-filter-label']}>
      {label}
      <div
        className={cn(
          styles['period-filter-inputs'],
          { disabled: isDisabled },
          className
        )}
      >
        <div className={styles['period-filter-begin-picker']}>
          <BaseDatePicker
            className={cn(
              styles['period-filter-input'],
              styles['field-date-begin']
            )}
            aria-label="Début de la période"
            disabled={isDisabled}
            maxDate={new Date(periodEndingDate)}
            minDate={minDateBeginning}
            onChange={event => onBeginningDateChange(event.target.value)}
            value={periodBeginningDate}
          />
        </div>

        <span className={styles['vertical-bar']} />

        <div className={styles['period-filter-end-picker']}>
          <BaseDatePicker
            className={cn(
              styles['period-filter-input'],
              styles['field-date-end']
            )}
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
