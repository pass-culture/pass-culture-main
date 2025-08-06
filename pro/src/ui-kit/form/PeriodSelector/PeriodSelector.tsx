import cn from 'classnames'

import { BaseDatePicker } from '@/ui-kit/form/shared/BaseDatePicker/BaseDatePicker'

import styles from './PeriodSelector.module.scss'

interface PeriodSelectorProps {
  className?: string
  onBeginningDateChange: (date: string) => void
  onEndingDateChange: (date: string) => void
  isDisabled?: boolean
  maxDateEnding?: Date
  minDateBeginning?: Date
  periodBeginningDate: string
  periodEndingDate: string
}

export const PeriodSelector = ({
  className,
  onBeginningDateChange,
  onEndingDateChange,
  isDisabled,
  maxDateEnding,
  minDateBeginning,
  periodBeginningDate,
  periodEndingDate,
}: PeriodSelectorProps) => (
  <div className={styles['period-filter']}>
    <div
      className={cn(
        styles['period-filter-inputs'],
        { disabled: isDisabled },
        className
      )}
    >
      <div className={styles['period-filter-begin-picker']}>
        <label htmlFor="field-date-begin" className={styles['visually-hidden']}>
          Début de la période
        </label>
        <BaseDatePicker
          className={cn(
            styles['period-filter-input'],
            styles['field-date-begin']
          )}
          disabled={isDisabled}
          maxDate={new Date(periodEndingDate)}
          minDate={minDateBeginning}
          onChange={(event) => onBeginningDateChange(event.target.value)}
          value={periodBeginningDate}
          id="field-date-begin"
        />
      </div>

      <span className={styles['vertical-bar']} />

      <div className={styles['period-filter-end-picker']}>
        <label htmlFor="field-date-end" className={styles['visually-hidden']}>
          Fin de la période
        </label>
        <BaseDatePicker
          className={cn(
            styles['period-filter-input'],
            styles['field-date-end']
          )}
          disabled={isDisabled}
          maxDate={maxDateEnding}
          minDate={new Date(periodBeginningDate)}
          onChange={(event) => onEndingDateChange(event.target.value)}
          value={periodEndingDate}
          id="field-date-end"
        />
      </div>
    </div>
  </div>
)
