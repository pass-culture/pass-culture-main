import classNames from 'classnames'
import { UseFormReturn } from 'react-hook-form'

import { OpeningHoursByWeekDayModel } from 'apiClient/v1'
import { weekDays } from 'components/IndividualOffer/StocksEventCreation/form/constants'
import { StocksCalendarFormValues } from 'components/IndividualOffer/StocksEventCreation/form/types'

import styles from './StocksCalendarFormOpeningHours.module.scss'
import { StocksCalendarFormOpeningHoursDay } from './StocksCalendarFormOpeningHoursDay/StocksCalendarFormOpeningHoursDay'

export function StocksCalendarFormOpeningHours({
  form,
}: {
  form: UseFormReturn<StocksCalendarFormValues>
}) {
  const days = Object.entries(form.watch('openingHours')).filter(
    ([, value]) => value.length > 0
  )

  return (
    <div className={styles['container']}>
      {days.map(([openingHourKey, openingHourValue], index) => {
        const dayLabel = weekDays.find((d) => d.value === openingHourKey)?.label
        return (
          <fieldset key={openingHourKey} className={styles['fieldset']}>
            <legend
              className={classNames(styles['legend'], {
                [styles['first-day']]: index === 0,
              })}
            >
              {dayLabel}
            </legend>
            <StocksCalendarFormOpeningHoursDay
              form={form}
              day={openingHourKey as keyof OpeningHoursByWeekDayModel}
              timespans={openingHourValue}
              dayIndex={index}
            />
          </fieldset>
        )
      })}
    </div>
  )
}
