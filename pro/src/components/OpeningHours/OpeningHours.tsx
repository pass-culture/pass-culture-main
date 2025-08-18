import classNames from 'classnames'
import { useFormContext } from 'react-hook-form'

import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import { mapDayToFrench, OPENING_HOURS_DAYS } from '@/commons/utils/date'

import styles from './OpeningHours.module.scss'
import { OpeningHoursTimespans } from './OpeningHoursTimespans/OpeningHoursTimespans'

export function OpeningHours() {
  const form = useFormContext<{
    openingHours: WeekdayOpeningHoursTimespans | null
  }>()

  const openingHours = form.watch('openingHours')

  return (
    <div className={styles['container']}>
      {OPENING_HOURS_DAYS.map((day) => {
        const dayHasTimespans = Boolean(
          openingHours?.[day] && openingHours[day].length > 0
        )

        const dayFrenchName = mapDayToFrench(day)
        return (
          <fieldset
            className={classNames(styles['fieldset'], {
              [styles['has-timespans']]: dayHasTimespans,
            })}
            key={day}
          >
            <legend className={styles['legend']}>{dayFrenchName}</legend>
            <div className={styles['timespans']}>
              <OpeningHoursTimespans
                weekDay={day}
                hasTimespans={dayHasTimespans}
                dayFrenchName={dayFrenchName}
              />
            </div>
          </fieldset>
        )
      })}
    </div>
  )
}
