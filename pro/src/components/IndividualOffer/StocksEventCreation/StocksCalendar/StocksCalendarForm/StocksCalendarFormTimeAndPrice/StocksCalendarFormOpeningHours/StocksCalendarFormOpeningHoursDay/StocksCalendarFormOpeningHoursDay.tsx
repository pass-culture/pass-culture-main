import { useFieldArray, UseFormReturn } from 'react-hook-form'

import { OpeningHoursByWeekDayModel, TimeSpan } from 'apiClient/v1'
import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'
import strokeLessIcon from 'icons/stroke-less.svg'
import strokeMoreIcon from 'icons/stroke-more.svg'
import { TimePicker } from 'ui-kit/formV2/TimePicker/TimePicker'
import { ListIconButton } from 'ui-kit/ListIconButton/ListIconButton'

import styles from './StocksCalendarFormOpeningHoursDay.module.scss'
import classNames from 'classnames'

export function StocksCalendarFormOpeningHoursDay({
  form,
  timespans,
  day,
  dayIndex,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
  timespans: TimeSpan[]
  day: keyof OpeningHoursByWeekDayModel
  dayIndex: number
}) {
  const { fields, append, remove } = useFieldArray({
    name: `openingHours.${day}`,
  })

  return (
    <div className={styles['container']}>
      <div className={styles['fields']}>
        {fields.map((f, index) => (
          <div key={f.id} className={styles['weekday-timespans']}>
            <TimePicker
              className={styles['time-slot']}
              label={
                <span
                  className={classNames({
                    [styles['visually-hidden']]: dayIndex !== 0 || index !== 0,
                  })}
                >
                  Ouvre à
                </span>
              }
              {...form.register(`openingHours.${day}.${index}.open`)}
              error={
                form.formState.errors?.openingHours?.[day]?.[index]?.open
                  ?.message
              }
            />
            <TimePicker
              className={styles['time-slot']}
              label={
                <span
                  className={classNames({
                    [styles['visually-hidden']]: dayIndex !== 0 || index !== 0,
                  })}
                >
                  Ferme à
                </span>
              }
              {...form.register(`openingHours.${day}.${index}.close`)}
              error={
                form.formState.errors?.openingHours?.[day]?.[index]?.close
                  ?.message
              }
            />
          </div>
        ))}
      </div>
      <div
        className={classNames({
          [styles['first-day-action']]: dayIndex === 0,
        })}
      >
        {timespans.length === 1 && (
          <ListIconButton
            icon={strokeMoreIcon}
            tooltipContent="Ajouter une plage horaire"
            onClick={() => {
              append({ open: '', close: '' })
            }}
          />
        )}
        {timespans.length === 2 && (
          <ListIconButton
            icon={strokeLessIcon}
            tooltipContent="Supprimer la plage horaire"
            onClick={() => {
              remove(1)

              const previousCloseInput = `openingHours.${day}.0.close`

              setTimeout(() => {
                console.log(
                  document.querySelector<HTMLInputElement>(
                    `[name="${previousCloseInput}"]`
                  )
                )
                document
                  .querySelector<HTMLInputElement>(
                    `[name="${previousCloseInput}"]`
                  )
                  ?.focus()
              })
            }}
          />
        )}
      </div>
    </div>
  )
}
