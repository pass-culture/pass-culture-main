import cn from 'classnames'
import { useId } from 'react'

import { BaseDatePicker } from '@/ui-kit/form/shared/BaseDatePicker/BaseDatePicker'

import styles from './PeriodSelector.module.scss'

interface PeriodSelectorProps {
  legend?: string
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
  legend,
  className,
  onBeginningDateChange,
  onEndingDateChange,
  isDisabled,
  maxDateEnding,
  minDateBeginning,
  periodBeginningDate,
  periodEndingDate,
}: PeriodSelectorProps) => {
  const ariaId = useId()

  return (
    <fieldset className={styles['period-filter']} disabled={isDisabled}>
      <legend
        className={cn({
          [styles['visually-hidden']]: legend === undefined,
        })}
      >
        {legend ?? 'Période'}
      </legend>
      <div className={cn(styles['period-filter-inputs'], className)}>
        <div className={styles['period-filter-begin-picker']}>
          <label
            htmlFor={`field-date-begin-${ariaId}`}
            className={styles['visually-hidden']}
          >
            Début de la période
          </label>
          <BaseDatePicker
            className={cn(
              styles['period-filter-input'],
              styles['field-date-begin']
            )}
            maxDate={new Date(periodEndingDate)}
            minDate={minDateBeginning}
            onChange={(event) => onBeginningDateChange(event.target.value)}
            value={periodBeginningDate}
            id={`field-date-begin-${ariaId}`}
          />
        </div>

        <div className={styles['period-filter-end-picker']}>
          <label
            htmlFor={`field-date-end-${ariaId}`}
            className={styles['visually-hidden']}
          >
            Fin de la période
          </label>
          <BaseDatePicker
            className={cn(
              styles['period-filter-input'],
              styles['field-date-end']
            )}
            maxDate={maxDateEnding}
            minDate={new Date(periodBeginningDate)}
            onChange={(event) => onEndingDateChange(event.target.value)}
            value={periodEndingDate}
            id={`field-date-end-${ariaId}`}
          />
        </div>
      </div>
    </fieldset>
  )
}
