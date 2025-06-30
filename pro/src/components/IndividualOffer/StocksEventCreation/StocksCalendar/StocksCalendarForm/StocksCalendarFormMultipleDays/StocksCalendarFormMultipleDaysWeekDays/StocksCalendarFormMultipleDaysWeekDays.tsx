import { useId } from 'react'
import { useFieldArray, UseFormReturn } from 'react-hook-form'

import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'
import { DayCheckbox } from 'ui-kit/form/DayCheckbox/DayCheckbox'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'

import styles from './StocksCalendarFormMultipleDaysWeekDays.module.scss'

export function StocksCalendarFormMultipleDaysWeekDays({
  form,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
}) {
  const { fields, update } = useFieldArray({
    name: 'multipleDaysWeekDays',
  })

  const errorId = useId()

  const groupErrors = form.formState.errors.multipleDaysWeekDays?.message

  return (
    <fieldset aria-describedby={errorId}>
      <legend className={styles['legend']}>Sélectionnez les jours : *</legend>
      <div className={styles['checkboxes']}>
        {fields.map((field, index) => {
          const weekDayValue = form.watch(`multipleDaysWeekDays.${index}`)

          return (
            <DayCheckbox
              name={`multipleDaysWeekDays.${index}`}
              key={field.id}
              label={weekDayValue.label[0]}
              className={styles['day-checkbox']}
              checked={weekDayValue.checked}
              tooltipContent={weekDayValue.label}
              error={groupErrors}
              displayErrorMessage={false}
              onChange={(e) => {
                update(index, {
                  ...weekDayValue,
                  checked: e.target.checked,
                })
              }}
            />
          )
        })}
      </div>
      <div role="alert" id={errorId}>
        {groupErrors && (
          <FieldError name="multipleDaysWeekDays" className={styles['error']}>
            {groupErrors}
          </FieldError>
        )}
      </div>
    </fieldset>
  )
}
