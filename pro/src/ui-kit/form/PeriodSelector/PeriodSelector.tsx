import cn from 'classnames'
import { useId } from 'react'

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
  errors?: {
    endingDate?: string
    beginningDate?: string
  }
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
  errors = { endingDate: '', beginningDate: '' },
}: PeriodSelectorProps) => {
  const ariaId = useId()

  return (
    <fieldset disabled={isDisabled}>
      <div className={cn(styles['period-filter-inputs'], className)}>
        <div className={styles['period-filter-inputs-datepicker']}>
          <label htmlFor={`field-date-begin-${ariaId}`}>Date de début</label>
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
            hasError={Boolean(errors.beginningDate)}
            aria-invalid={Boolean(errors.beginningDate)}
          />
          {errors.beginningDate && (
            <p className={styles['field-date-error']}>{errors.beginningDate}</p>
          )}
        </div>

        <div className={styles['period-filter-inputs-datepicker']}>
          <label htmlFor={`field-date-end-${ariaId}`}>Date de fin</label>
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
            hasError={Boolean(errors.endingDate)}
            aria-invalid={Boolean(errors.endingDate)}
          />
          {errors.endingDate && (
            <p className={styles['field-date-error']}>{errors.endingDate}</p>
          )}
        </div>
      </div>
    </fieldset>
  )
}
